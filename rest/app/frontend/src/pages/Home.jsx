import { useRef, useState } from 'react';
import { Form, redirect, useNavigation } from 'react-router-dom';
import Loading from '../components/Loading';

export async function submitTask({request, params}) {
    const formData = await request.formData();
    const updates = Object.fromEntries(formData);
    console.log(updates);
    const task = { id: 10 };
    return redirect(`/app/task/${task.id}`);
}

function Home() {
	const navigation = useNavigation();
	const [inputTypeFile, setInputTypeFile] = useState(true);
	const [file, setFile] = useState(null);
	const [inputText, setInputText] = useState('');

	const crackingTypes = ['Single', 'Incremental', 'Wordlist'];
	const [selectedCrack, setSelectedCrack] = useState(0);

	const wordlist = ['a', 'bbbbbbbbbbbbbbbbbbbbbbbbbbb', 'c'];
	const [selectedWordlist, setSelectedWordlist] = useState(0);

	const changeInputFile = (event) => {
		setFile(event.target.files[0]);
	}

	const changeInputText = (event) => {
		setInputText(event.target.value);
	}

	const changeCrackingType = (event) => {
		setSelectedCrack(event.target.value);
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
								className='button fileInput'
								type="file"
								id="file"
								name="file"
								required
								onChange={changeInputFile}
							/>
							<label className='button' htmlFor='file'>Choose file</label>
							<span className='fileName'>{file ? file.name : "No file"}</span>
						</div>
						: <div className='hashInput textInput'>
							<textarea
								onChange={changeInputText}
								value={inputText}
								style={{ width: 500, height: 150, padding: 8 }}
							/>
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
				<input type="submit" className='button button-primary' value='Submit task' />
			</Form>
      {navigation.state != 'idle' && <Loading />}
		</div>
	)
}

export default Home;
