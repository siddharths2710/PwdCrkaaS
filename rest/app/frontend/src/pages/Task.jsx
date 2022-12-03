import React from 'react';
import { useLoaderData } from 'react-router-dom';
import { useTimedState } from '../helper';

async function getTaskDetails({ params }) {
  const url = '/api/v1/task-details?' + new URLSearchParams(params);
  let response = await fetch(url);

  if (response.status != 200) {
    // Show the error page
    let errorMessage = await response.json();
    throw Error(errorMessage.error || 'Failed to submitted the task');
  }
  return await response.json();
}

export async function taskLoader({ request, params }) {
  // const taskId = params.taskId;
  const task = await getTaskDetails({ request, params });
  return { task };
}

async function terminateTask(taskId) {
  const url = '/api/v1/terminate-task?' + new URLSearchParams({ taskId });
  const resp = await fetch(url);
  return await resp.json();
}

export default function Task() {
  const [copied, setCopied] = useTimedState(false, 3000);
  const [terminating, setTerminating] = useTimedState(false, 6000);
  const { task } = useLoaderData();

  const copyUrl = (() => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
  })

  const terminate = () => {
    terminateTask(task.id);
    setTerminating(true);
  }

  return (
    <div>
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

      {task.status == 'pending' && <div>Task is yet to be started</div>}
      {task.status == 'progress' && <div>Task is in progress</div>}
      {task.status == 'done' && <div>Task completed</div>}

      <button
        className={
          'button button-terminate ' +
          (task.status != 'progress' || terminating ? 'disabled' : '')
        }
        disabled={task.status != 'progress' || terminating}
        onClick={terminate}
      >{terminating ? "Terminating" : "Terminate"}</button>

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
