# Password Cracking as a Service (PwdCrkaaS)

  

Intuitive password cracking service over the cloud using K8S, React and Object Storage

  

## Team Members

|Name|Identikey|Affiliation|Course Code
|--|--|--|--|
|Shreyash Sarnayak|shsa2077|Graduate (MSCPS)|CSCI 5253-003|
|Siddharth Srinivasan|sisr9857|Graduate (MSCPS)|CSCI 5253-001|

## Tech Stack
- Kubernetes cluster configs for deployment specification
- React for frontend
- Python/Flask for rest service
- Python for the backend worker services, and logging service
- Redis for **session management** and **message queue** implementation
- MySQL for storing relevant information and metadata for request and output
  

## Project Goals
- Provide a Password-Cracking Service
	- Cloud-Based Scalable Solution handling several user sessions
	- Simple and intuitive, user-friendly GUI/RESTful APIs
- Cracking modes offered (Revised from **PROPOSAL**):
    - **Single-crack** Mode: Uses default login names, Full Name Fields and users' home directory names as candidate passwords, with a large set of mangling rules applied.
    - **Incremental** Mode: Permutes through all possible characters/numbers while building up a password within a minimum and maximum length bound. More exhaustive and inefficient, but powerful nonetheless.
    -  **Wordlist** Mode: Provide the service with a list of (commonly-used) passwords leaked from data breaches/collated as wordlists, and apply every single phrase in an attempt to find the correct one
- Primary goal is to accept a list of hashes which represent the passwords to be cracked, and to delegate the compute to the workers towards retrieving the passwords.
    ![Cracking_Workflow](https://bestestredteam.com/content/images/2018/08/image-6.png)
- **Transparency**: Previous cracked passwords maintained and made openly available for consumption by others, to leverage the affinity of users with a select few commonly-used set of passwords used. This works towards the efficiency of our solution since unnecessary pre-computations can be avoided.

## Overview

A typical request-response workflow can be summarized as follows:
- End user provides the following parameters for password cracking
    - A list of hashes to be cracked
    - Cracking mode (Single, incremental or wordlist)
    - Wordlist file if applicable

![User_Input](https://i.imgur.com/YOcDELH.jpg)

- Based on his settings, a worker is allocated to handle the task in the backend, and a list of passwords cracked is presented to him when
    - the worker finishes the cracking process, OR
    - the user wishes to terminate the job in the interest of time, using the `TERMINATE` button
![Password_Output](https://i.imgur.com/gqQMc43.jpg)

#### REST API interface

Along with the Website we also provide a REST API Interface.


Url | Method | Desc
--  | ----  | ----
/api/v1/crack | POST | The main API which starting the password cracking task
/api/v1/wordlist | GET | Returns the already existing wordlist
/api/v1/task-details | GET | Gets the task details like cracked passwords and status (pending, running, completed)
/api/v1/terminate-task | GET | Schedule the running task for cancellation.
/api/v1/pending-task | GET | Lists all the task in the queue. Tasks yet to be run by the worker.


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
- Usage of queues for message passing
	- One to track the work requested by several users, to be processed once a worker becomes available (`worker_queue`)
	- Another to track the series of logs dispatched across instances to be logged by the logging service (`logging_queue`)
    - A third queue ( `terminate_queue`) to notify when user wishes to terminate his password-cracking job (This becomes essential as password cracking is a time-consuming process, and user might wish to retrieve the set of cracked passwords at a given instant in time.
- A `Relational Database` maintaining couple of frequently used tables
    - A User table storing details of request data sent by the end user, and the request status:
    - An output table maintaining cracked passwords associated with a user who triggered the job
```
	CREATE Table User_Inputs (
    	UserID UUID NOT NULL,
        CrackingMode VARCHAR(12) NOT NULL,
        HashFile VARCHAR(40) NOT NULL,
        WordlistFile VARCHAR(40),
        HashType VARCHAR(12) DEFAULT 'crypt',
        Status VARCHAR(10) DEFAULT 'pending',
        PRIMARY_KEY(UserID)
    );
```
    
```
    CREATE Table Password_Outputs (
       UserID UUID NOT NULL,
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

## Debugging and Troubleshooting
- Our `log_svc` consolidates functioning specific logs aggregated from all design components in one single roof. This enables us to get a holistic report of the workings of our solution.
- Any abnormal behavior unexplained by `log_svc` is handled in the following manner:
    - If a component is not reachable, we inspect its setup and test connectivity manually
    - Inspect development logs of a component in case it hasn't been setup to function
    - If a component is setup but doesn't perform it's function, we'd login remotely to that component and validate if the configurations are in accordance with our expectation. This is only if `log_svc` doesn't report anything for us.

## Validation and Testing

- For `single` and `incremental` modes, we evaluate our solution using hashes of short, weak and easily-to-compute passwords to evaluate our system.
- For the more popular `wordlist` mode, we either generate our own list of common passwords that serve as a wordlist, or leverage an already popular source such as [RockYou WordList](https://archive.org/details/rockyou.txt).


### Capabilities
The system is designed to scale the workers and the rest-services alike.
- The advantage of scaling the webapp (rest) services is to handle more requests from end users for password cracking, and queue them for consumption by available workers
- Correspondingly, more jobs can be handled by simply dispatching more workers, which can serve a job waiting in the task queue.
- Multiple concurrent Database writes are handled through the concept of ACID transactions
	- Only successful commits make data visible to other users
	- Concurrent transactions don’t interfere with one another
### Bottlenecks
- The cracking modes are currently restrictive, since our system doesn't provide modes that are otherwise typically offered:
    - **Hybrid**: Dependence on two or more existing modes for password generation. Ex. Deriving the first half of a candidate from a wordlist, and auto-generating the second half incrementally.
    - **Rainbow Tables**: Pre-computed hashes maintained for a large dictionary/wordlist set. This requires a considerable amount of storage in the backend, but makes the cracking process more efficient.
    - **Mangling Rules**: Provision for a set of rules that dictate how password-combinations are computed and/or clubbed with other modes of cracking.
- While we can scale the gateway services to handle several concurrent requests, and deploy several workers to handle the corresponding jobs, the **CPU compute power** and **memory utilization of the workers** serve as a largely limiting factor for efficacy and performance, since password cracking is predominantly compute intensive and depends on memory flushing for updating cracked passwords. 
    - This means that a single worker handling several cracking tasks for a single user could likely be bottlenecked sooner than we expect. This is mainly because the underlying password cracking utility has severe resource demands especially when cracking must be performed smoothly. A cracking job could take several days for completion, depending on the number of password hashes in a request and st	rength of each password.
    - Several GPU-based cracking utilities are now available, but leveraging the same in a containerized environment has several complications setting up and running. This serves as a future goal towards efficient cloud-based password cracking.
