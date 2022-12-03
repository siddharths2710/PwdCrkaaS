import React, { useState } from 'react';

export default function HashInput({ errors }) {
    const [inputTypeFile, setInputTypeFile] = useState(true);
    const [file, setFile] = useState(null);
    const [inputText, setInputText] = useState('');

    const changeInputFile = (event) => {
        setFile(event.target.files[0]);
    }

    const changeInputText = (event) => {
        setInputText(event.target.value);
    }

    return (
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
                    <label
                        className={'button ' + (errors?.name == 'hashFile' ? 'errorBorder' : '')}
                        htmlFor='file'
                    >Choose file</label>
                    <span className={'fileName'}>{file ? file.name : "No file"}</span>
                </div>
                : <div className='hashInput textInput'>
                    <textarea
                        onChange={changeInputText}
                        name="hashText"
                        value={inputText}
                        className={errors?.name == 'hashText' ? 'errorBorder' : ''}
                        style={{ width: 500, height: 150, padding: 8 }}
                    />
                </div>
            }
        </div>
    )
}