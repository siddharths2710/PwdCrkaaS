import { useState } from 'react';
import './App.css';

function App() {
  const [count, setCount] = useState(0);
  const [inputTypeFile, setInputTypeFile] = useState(true);
  const [file, setFile] = useState(null);

  const crackingTypes = ['Single', 'Incremental', 'Wordlist'];
  const [selectedCrack, setSelectedCrack] = useState(0);

  const wordlist = ['a', 'bbbbbbbbbbbbbbbbbbbbbbbbbbb', 'c'];
  const [selectedWordlist, setSelectedWordlist] = useState(0);

  const changeInputFile = (event) => {
    setFile(event.target.files[0]);
  }

  const changeCrackingType = (event) => {
    setSelectedCrack(event.target.value);
  }

  const changeWordlist = (event) => {
    setSelectedWordlist(event.target.value);
  }

  return (
    <div className="App">
      <h1>Password Cracking as a Service</h1>
      <form>
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
          {/* <button className='button' onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button> */}
          {inputTypeFile
            ? <div className='hashInput fileInput'>
                <input type="file" id="file" name="file" hidden onChange={changeInputFile}/>
                <label className='button' htmlFor='file'>Choose file</label>
                <span className='fileName'>{file ? file.name : "No file"}</span>
              </div>
            : <div className='hashInput textInput'>
                text here
              </div>
          }
        </div>
        <div className="card">
          <h3 className='crackingLabel'>Choose a cracking method</h3>
          <select className='button' id="crackingType" value={selectedCrack} onChange={changeCrackingType}>
            {crackingTypes.map((cType, i) => (
              <option key={cType} value={i}>{cType}</option>
            ))}
          </select>
          {crackingTypes[selectedCrack] == 'Wordlist' &&
            <div className='wordlistChoice'>
              <h3 className='wordlistLabel'>Choose a wordlist</h3>
              <select className='button' id="wordlist" value={selectedWordlist} onChange={changeWordlist}>
                {wordlist.map((name, i) => (
                  <option key={name} value={i}>{name}   </option>
                ))}
              </select>
            </div>
          }
        </div>
        <input type="submit" className='button button-primary' value='Submit task'/>
      </form>
    </div>
  )
}

export default App
