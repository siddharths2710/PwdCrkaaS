import React, { useState } from "react";

export default function Wordlist({ wordlist, errors }) {
  const [selectedWordlist, setSelectedWordlist] = useState("");

  const changeWordlist = (event) => {
    setSelectedWordlist(event.target.value);
  };

  if (!wordlist) {
    return (
      <div className='wordlistChoice'>
        Loading wordlist...
        <input
          className={'hiddenInput ' + (errors?.name == 'hashFile' ? 'errorBorder' : '')}
          name='wordlist'
          required
        />
      </div>
    )
  }
  return (
    <div className='wordlistChoice'>
      <h3 className='wordlistLabel'>Choose a wordlist</h3>
      <select
        className='button'
        id="wordlist"
        name="wordlist"
        value={selectedWordlist}
        onChange={changeWordlist}
        required
      >
        <option value="">Select a wordlist</option>
        {wordlist.map((name) => (
          <option key={name} value={name}>{name}</option>
        ))}
      </select>
    </div>
  )
}
