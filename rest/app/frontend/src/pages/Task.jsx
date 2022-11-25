import { useRef, useState } from 'react';
import { redirect, useLoaderData, useNavigation } from 'react-router-dom';

function getTaskDetails(taskId) {
  return new Promise((res, rej) => {
    let passwords = [
      // { hash: 'aaaa', password: 'bbbb', hash_type: 'crypt', salt: 'ddd' }
    ];
    setTimeout(() => res({ id: taskId, passwords }), 1000);
  })
}

export async function taskLoader({ params }) {
  const taskId = params.taskId;
  const task = await getTaskDetails(taskId);
  return { task };
}

export default function Task() {
  // const navigation = useNavigation();
  const { task } = useLoaderData();
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
              : task.passwords.map((pwd, i) => (
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
          <button className='button button-copy'>Copy!</button>
        </span>
      </p>
    </div>
  )
}

