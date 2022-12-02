import React, { useEffect, useRef } from 'react';
import { useState } from 'react';
import { useLoaderData } from 'react-router-dom';

async function getTaskDetails({ request, params }) {
  // return new Promise((res, rej) => {
  //   let passwords = [
  //     // { hash: 'aaaa', password: 'bbbb', hash_type: 'crypt', salt: 'ddd' }
  //   ];
  //   setTimeout(() => res({ id: taskId, passwords }), 1000);
  // })
  const url = '/api/v1/task-details?' + new URLSearchParams(params);
  let data = await fetch(url);
  // console.log(data);
  // console.log(request);
  // console.log(params);
  return await data.json();
}

export async function taskLoader({ request, params }) {
  // const taskId = params.taskId;
  const task = await getTaskDetails({ request, params });
  return { task };
}

export default function Task() {
  // const navigation = useNavigation();
  const [copied, setCopied] = useState(false);
  const { task } = useLoaderData();
  const copyTimer = useRef(undefined);

  const copyUrl = (() => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    copyTimer.current = setTimeout(() => {
      setCopied(false);
      copyTimer.current = undefined;
    }, 3000);
  })

  useEffect(() => {
    return () => {
      if (copyTimer.current) {
        clearTimeout(copyTimer.current);
      }
    }
  }, []);

  return (
    <div>
      {/* task view here id={task.id} */}
      <h1>Password cracking task</h1>

      <p>Following are the passwords that have been recovered</p>
      <div className='tableWrapper'>
        <table>
          <thead>
            <tr>
              <th>Hash</th>
              <th>Password</th>
              <th>Hash type</th>
              <th>Salt</th>
            </tr>
          </thead>
          <tbody>
            {(!task.passwords || task.passwords.length == 0)
              ? <tr><td colSpan={4}>No passwords have been recovered.</td></tr>
              : task.passwords.map((pwd) => (
                <tr key={pwd.hash}>
                  <td>{pwd.hash}</td>
                  <td>{pwd.password}</td>
                  <td>{pwd.hash_type}</td>
                  <td>{pwd.salt}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <button className='button'>Interrupt</button>

      <p>
        <span>Remember this url:{" "}</span>
        <span className='urlBoxWrapper'>
          <span className='urlBox'>{window.location.href}</span>
          <button
            className='button button-copy'
            onClick={copyUrl}
          >{copied ? 'Copied!' : 'Copy!'}</button>
        </span>
      </p>
    </div>
  )
}

