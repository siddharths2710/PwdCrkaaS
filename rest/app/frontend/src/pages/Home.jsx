import React, { useEffect } from 'react';
import { useState } from 'react';
import { Form, redirect, useActionData } from 'react-router-dom';

export async function submitTask({ request, params }) {
  const formData = await request.formData();
  // const updates = Object.fromEntries(formData);
  // console.log(updates);
  let response = await fetch('/api/v1/crack', {
    method: 'POST',
    body: formData
  });

  if (response.status == 400) {
    return await response.json();
  } else if (response.status != 200) {
    throw Error('Failed to submitted the task');
  }

  const task = await response.json();
  return redirect(`/app/task/${task.id}`);
}

function Wordlist({ wordlist, selectedWordlist, changeWordlist }) {
  if (!wordlist) {
    return (
      <div className='wordlistChoice'>
        Loading wordlist...
        <input className='hiddenInput' name='wordlist' required />
      </div>
    )
  }
  return (
    <div className='wordlistChoice'>
      <h3 className='wordlistLabel'>Choose a wordlist</h3>
      <select className='button' id="wordlist" name="wordlist" value={selectedWordlist} onChange={changeWordlist}>
        {wordlist.map((name, i) => (
          <option key={name} value={i}>{name}</option>
        ))}
      </select>
    </div>
  )
}

function getWordlist(wordlist) {
  return new Promise((res, rej) => {
    setTimeout(() => res(wordlist), 3000);
  })
}

function Home() {
  const [inputTypeFile, setInputTypeFile] = useState(true);
  const [file, setFile] = useState(null);
  const [inputText, setInputText] = useState('');

  const hashTypes = ['crypt', 'md5'];
  const [selectedHashType, setSelectedHashType] = useState(0);

  const crackingTypes = ['Single', 'Incremental', 'Wordlist'];
  const [selectedCrack, setSelectedCrack] = useState(0);

  // const wordlist = ['a', 'bbbbbbbbbbbbbbbbbbbbbbbbbbb', 'c'];
  const [wordlist, setWordlist] = useState(null);
  const [selectedWordlist, setSelectedWordlist] = useState(0);

  const errors = useActionData();
  console.log({ errors });

  useEffect(() => {
    getWordlist(['a', 'bb', 'c']).then(wordlist => {
      setWordlist(wordlist);
    })
  })

  const changeInputFile = (event) => {
    setFile(event.target.files[0]);
  }

  const changeInputText = (event) => {
    setInputText(event.target.value);
  }

  const changeCrackingType = (event) => {
    setSelectedCrack(event.target.value);
  }

  const changeHashType = (event) => {
    setSelectedHashType(event.target.value);
  }

  const changeWordlist = (event) => {
    setSelectedWordlist(event.target.value);
  };

  return (
    <div className="App">
      <h1>Password Cracking as a Service</h1>
      <Form method='post' encType="multipart/form-data">
        <div className="card">
          <h3 className='inputTypeHeading'>Choose the hash</h3>
          <span className='inputTypeWrapper'>
            <input
              type="radio"
              id="inputFile"
              name="inputType"
              value="file"
              checked={inputTypeFile}
              onChange={() => setInputTypeFile(true)}
            />
            <label className='button' htmlFor='inputFile'>Input from a file</label>
          </span>
          <span className='inputTypeWrapper'>
            <input
              type="radio"
              id="inputText"
              name="inputType"
              value="text"
              checked={!inputTypeFile}
              onChange={() => setInputTypeFile(false)}
            />
            <label className='button' htmlFor='inputText'>Input from a text</label>
          </span>
          {inputTypeFile
            ? <div className='hashInput fileInputDiv'>
              <input
                className='button hiddenInput'
                type="file"
                id="file"
                name="hashFile"
                required
                onChange={changeInputFile}
              />
              <label className='button' htmlFor='file'>Choose file</label>
              <span className='fileName'>{file ? file.name : "No file"}</span>
            </div>
            : <div className='hashInput textInput'>
              <textarea
                onChange={changeInputText}
                name="hashText"
                value={inputText}
                style={{ width: 500, height: 150, padding: 8 }}
              />
            </div>
          }
        </div>
        <div className="card">
          <h3 className='crackingLabel'>Choose the hash type (crypt for unknown)</h3>
          <select className='button' id="hashType" name="hashType" value={selectedHashType} onChange={changeHashType}>
            {hashTypes.map((hType, i) => (
              <option key={hType} value={i}>{hType}</option>
            ))}
          </select>
          <h3 className='crackingLabel'>Choose a cracking method</h3>
          <select className='button' id="crackingType" name="crackingType" value={selectedCrack} onChange={changeCrackingType}>
            {crackingTypes.map((cType, i) => (
              <option key={cType} value={i}>{cType}</option>
            ))}
          </select>
          {crackingTypes[selectedCrack] == 'Wordlist' &&
            <Wordlist
              wordlist={wordlist}
              selectedWordlist={selectedWordlist}
              changeWordlist={changeWordlist}
            />
          }
        </div>
        <input type="submit" className='button button-primary' value='Submit task' />
      </Form>
    </div>
  )
}

export default Home;
