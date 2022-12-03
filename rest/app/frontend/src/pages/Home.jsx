import React, { useEffect } from 'react';
import { useState } from 'react';
import { Form, redirect, useActionData } from 'react-router-dom';
import HashInput from '../components/HashInput';
import Wordlist from '../components/Wordlist';

export async function submitTask({ request }) {
  const formData = await request.formData();
  let response = await fetch('/api/v1/crack', {
    method: 'POST',
    body: formData
  });

  if (response.status == 400) {
    // Show the error on the form
    return await response.json();
  } else if (response.status != 200) {
    // Show the error page
    let errorMessage = await response.json();
    throw Error(errorMessage.error || 'Failed to submitted the task');
  }

  const task = await response.json();
  return redirect(`/app/task/${task.id}`);
}

async function getWordlist() {
  const resp = await fetch('/api/v1/wordlist');
  if (resp.status != 200) {
    throw new Error('Failed to load the home page');
  }
  return await resp.json();
}

function Home() {
  const hashTypes = ['crypt', 'md5'];
  const [selectedHashType, setSelectedHashType] = useState(hashTypes[0]);

  const crackingTypes = ['single', 'incremental', 'wordlist'];
  const [selectedCrack, setSelectedCrack] = useState(crackingTypes[0]);

  const [wordlist, setWordlist] = useState(null);

  const errors = useActionData();

  useEffect(() => {
    getWordlist().then(wordlist => {
      setWordlist(wordlist);
    })
  }, [])

  const changeCrackingType = (event) => {
    setSelectedCrack(event.target.value);
  }

  const changeHashType = (event) => {
    setSelectedHashType(event.target.value);
  }

  return (
    <div className="App">
      <h1>Password Cracking as a Service</h1>
      <Form method='post' encType="multipart/form-data">
        <div className="card">
          <HashInput errors={errors} />
          <h3 className='crackingLabel'>Choose the hash type (crypt for unknown)</h3>
          <select className='button' id="hashType" name="hashType" value={selectedHashType} onChange={changeHashType}>
            {hashTypes.map((hType) => (
              <option key={hType} value={hType}>{hType}</option>
            ))}
          </select>
          <h3 className='crackingLabel'>Choose a cracking method</h3>
          <select className='button' id="crackingType" name="crackingType" value={selectedCrack} onChange={changeCrackingType}>
            {crackingTypes.map((cType) => (
              <option key={cType} value={cType}>{cType}</option>
            ))}
          </select>
          {selectedCrack == 'wordlist' &&
            <Wordlist
              wordlist={wordlist}
              errors={errors}
            />
          }
        </div>
        {errors &&
          <div className='card errorBoxWrapper'>
            <div className='errorBox'>
              <svg xmlns="http://www.w3.org/2000/svg" className='xIcon' viewBox="0 0 24 24">
                <path d="M24 20.188l-8.315-8.209 8.2-8.282-3.697-3.697-8.212 8.318-8.31-8.203-3.666 3.666 8.321 8.24-8.206 8.313 3.666 3.666 8.237-8.318 8.285 8.203z" />
              </svg>
              <span className='errorMessage'>{errors.error}</span>
            </div>
          </div>
        }
        <input type="submit" className='button button-primary' value='Submit task' />
      </Form>
    </div>
  )
}

export default Home;
