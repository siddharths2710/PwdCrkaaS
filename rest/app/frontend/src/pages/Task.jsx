import { useRef, useState } from 'react';
import { redirect, useLoaderData, useNavigation } from 'react-router-dom';

function getTaskDetails(taskId) {
  return new Promise((res, rej) => {
    setTimeout(() => res({ id: taskId }), 1000);
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
      task view here id={task.id}
    </div>
  )
}

