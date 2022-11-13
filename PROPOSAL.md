# Password Cracking as a Service (PwdCrkaaS)

  

Intuitive password cracking service over the cloud

  

## Team Members

|Name|Identikey|Affiliation|Course Code
|--|--|--|--|
|Shreyash Sarnayak|shsa2077|Graduate (MSCPS)|CSCI 5253-003|
|Siddharth Srinivasan|sisr9857|Graduate (MSCPS)|CSCI 5253-001|

  

## Project Goals
- Central idea is to design and build a password-cracking service over the cloud that is intuitive to use using a user-friendly GUI and simplified RESTful APIs
    - Typical password cracking utilities provide different modes for going about cracking passwords:
	    - **Brute Force**: Permutes through all possible characters/numbers while building up a password within a minimum and maximum length bound
	    -  **Dictionary Attack**: Provide the service with a list of (commonly-used) passwords leaked from data breaches/collated as wordlists, and apply every single phrase in an attempt to find the correct one
	    - **Hybrid Attack**: A combination of generating password using wordlists and brute force output appended to each traversed word
	    - **Rainbow Tables**: Most backends nowadays store password hashes of a fixed length instead of the password itself. In this mechanism, we maintain a pre-computed list of possible password hashes against an existing source instead of a dictionary itself. Faster than a dictionary and brute-force attacks.
    - Primary goal is to simplify the parameters passed to such modes by providing a simplified, straightforward and *easy to understand* user interface.
- Another goal is transparency, i.e previous cracked passwords maintained and made openly available for consumption by others, to leverage the affinity of users with a select few commonly-used set of passwords used. This works towards the efficiency of our solution since unnecessary pre-computations can be avoided.
## Project Components
[//]: # (A _**specific**_ list of software and hardware components)
- Client with either a Kubernetes installation, or a registration with a kubernetes cloud service
- Ingress controller (preferably Nginx-based for local deployment, or cloud-native specification)
- Service pod for running the Gateway interface (WSGI Service)
- Cluster of **Web/RESTful based application servers** processing incoming requests
- Lookup store for maintaining **User Sessions** (with periodic persistence)
- Two object store-based buckets
	- For maintaining publicly made/privately uploaded **Wordlists** to test the password hash against
	- For maintaining the password files uploaded by the user
- Cluster of **Workers** for processing the password cracking implementation
- Service for consolidated **log reporting** across instances 
- Couple of queues
	- One to track the work requested by several users, to be processed once a worker becomes available (`worker_queue`)
	- Another to track the series of logs dispatched across instances to be logged by the logging service (`logging_queue`)
- A `Relational Database` maintaining outputs of successful password cracking attempts with the below schema:

```
    CREATE Table Password_Outputs (
       UserID INTEGER NOT NULL,
       Hash   VARCHAR(40) NOT NULL,
       Password VARCHAR(40) NOT NULL,
       HashType VARCHAR(10) NOT NULL,
       Salt VARCHAR(20) NOT NULL,
       PRIMARY_KEY(UserID, Hash, HashType)
    );
```

## Architectural Diagram

![Imgur](https://i.imgur.com/FBNgDAj.jpg)

[//]: # (https://medium.com/the-internal-startup/how-to-draw-useful-technical-architecture-diagrams-2d20c9fda90d)

[//]: # (A description of the interaction of the different software and hardware components)

### Interactions between hardware and software
- Client issues a request for cracking passwords, and the ingress controller forwards the same to the appropriate WSGI gateway service that in turn forwards the request to the `webapp_server` that is available and appropriate enough to handle the request (based on endpoint hit).
- The `webapp_server` handles different requests differently
    - The most common input we expect is the list of password hashes captured by the client as input. In this case, we first store these in a dedicated `input_hashes` bucket before proceeding to dispatch a job to the workers.
    - In addition to this, we allow the user to either decide on testing the hashes against popular wordlists (fetched directly from the `input_wordlists` bucket) or allow the client to provide their own wordlist file to be stored in `input_wordlists` instead (since client could possibly have a rough idea of the password pattern).
    - Regardless, all password cracking requests are sent to the `worker_queue`, so that an available `worker` can take up a task from the queue and work accordingly.
    - Once the `webapp_server` dispatches the above work request, it also sends a cookie to the client back, which maintains the `user_id` which the client can use to retrieve the status of his request, and obtain the result later on. This is maintained from the server-side using a fast, volatile `user_session` store.
- Once the worker is done with his job, he 
    - alerts the `webapp_server` on the completion status, 
    - stores the output file (if any) in an output bucket (to be returned to the client)
    - Also maintains the record of cracked passwords in the `passwords_output` DB for future introspection (Lookup Table optimization).
- The components (ingress, services, webapp_servers, workers etc.) are responsible to emit logs indicating the status of their operations. We maintain a `logging_queue` for the components to queue in their logs, which are consumed by logging services and reported to engineers on the other side.

## Debugging, Validation and Troubleshooting
- Most of our component functioning details will be consolidated by our `log_svc`, hence we plan to attach a console for analyzing the growing `log_svc` log output.
- Any abnormal behavior unexplained by `log_svc` will be handled in the following manner:
    - If a component is not reachable, we inspect its setup and test connectivity manually
    - Inspect development logs of a component in case it hasn't been setup to function
    - If a component is setup but doesn't perform it's function, we'd login remotely to that component and validate if the configurations are in accordance with our expectation. This is only if `log_svc` doesn't report anything for us.
- We will test our system against a popular wordlist (Ex. [RockYou wordlist](https://archive.org/details/rockyou.txt)) by creating a small sample of the input hashes associated with few password present in the list. 

## Meeting Project Requirements
Our project is holistic enough to leverage enough datacenter-scale components to justify the requirements:
- **Interfaces (API/RPC)** will be exposed to the client for consumption. In addition, a plan to devise a user-friendly **GUI** is also in place, for making the experience more intuitive than using password-cracking tools directly.
- Data transmission is a major requirement, which we address using **marshalling and encoding primitives** in fetching the hash/wordlist files required, transmitting them across components and ultimately send output to the client as well.
- To maintain a fair priority in handling requests and prevent worker/logger overload, we maintain `message queues` which track requests waiting to be processed to be consumed when a worker is available.
- We maintain a `Password_Outputs` database tracking already cracked passwords to be reused for subsequent password-cracking requests.
- We're planning to maintain `user_ids` in a temporary fast-lookup store like Redis for tracking user sessions.
- We leverage **containers** as the `computing` unit for every component involved in data and task processing.
- Finally, we plan to use a storage service for the `input_hashes`, `input_wordlists` and `output_file` per client job.

## Rubric FAQs

> Is the proposed project interesting to you or does it seem a joyless effort? Explain why or why not.

Password cracking as a utility isn't novel, since its concepts (check **Project Goals**) were standardized by the ethical hacking community well in the past. That being said, delivering the service through an end-to-end system of components served over the cloud is expected to be challenging due to the following reasons:
- The functionality to pause and restore password cracking (offered by most utilities). This is essential since the end user might wish to foresee the partial list of cracked passwords to take a call on whether he/she wishes to perform the same operation on the remaining hashes as well. 
- The possibility of tailoring the compute, storage and resource requirement based on the hash strength/dictionary size, the wordlist or the lookup table size to be checked against, possiblity of salting, permuting against password combinations in a brute-force setting etc.
- The possiblity of accomodating combinator/mangling rules written in configs/programming languages. This feature is to be used in tandem with wordlists to provide variation against existing passwords specified in the wordlist. We wish to take a call on accomodating this feature depending on complexity of the underlying utility we stick to.
- It is difficult/tricky enough to accomodate every single CLI switch/utility option into our GUI/APIs, but we are focusing at the moment to deliver a simplified and a rather understandable interface for the time being.

> Do you believe this project idea will meet the eventual project requirements (use of different cloud technologies)? If not, explain your concern.

We believe that this is easily satisfied while describing our architecture and interactions between components. At this point, we're hoping to cover:
- Message marshalling / encoding
- RPC / API interfaces
- Message queues
- Databases
- Key-Value Stores
- Containers or "functions as a service"
- Storage services (s3, etc)

> Do you think the project is within scope for the class? Is it too ambitious? Too conservative?

Each of us had different project ideas, and amongst us, we believe that the [Online Vulnerability Scanner](https://piazza.com/class/l6vfpvp6y966r0/post/105) idea that one of us proposed is rather too ambitious since this would require more deliberation in tackling several unknowns we cannot being to fathom! 

For the current topic that we've settled, we were planning on offering subscription tiers where users can opt for more compute or autoscaling upto a fixed number of workers towards faster cracking of passwords, but we reasoned that this could be very ambitious for this project deliverable.

We believe that the typical constructs of datacenter components are a necessity for achieving our password cracking project, and that alone simply makes it within the scope of what's being taught in class.

[//]: # (A description of **how you will debug your proposed project** and what training or testing mechanism will be used.)

[//]: # (Explain why you believe this project idea will meet the eventual project requirements; use of four different cloud technologies)

[//]: # (More on https://moodle.cs.colorado.edu/mod/page/view.php?id=55973)
