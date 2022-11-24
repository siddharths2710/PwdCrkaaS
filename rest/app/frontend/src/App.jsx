import {
  createBrowserRouter,
  RouterProvider,
  Route,
} from "react-router-dom";

import Home, { submitTask } from './pages/Home';
import Task, { taskLoader } from "./pages/Task";
import ErrorPage from './pages/Error';

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
    errorElement: <ErrorPage />,
    action: submitTask
  },
  // {
  //   path: "/submit",
  //   action: submitTask
  // },
  {
    path: "/app/task/:taskId",
    element: <Task />,
    loader: taskLoader
  }
]);

function App() {
  return (
    <RouterProvider router={router} />
  );
}

export default App
