import {
  createBrowserRouter,
  RouterProvider,
  Route,
  Outlet,
  useNavigation,
} from "react-router-dom";

import Home, { submitTask } from './pages/Home';
import Task, { taskLoader } from "./pages/Task";
import ErrorPage from './pages/Error';
import Loading from "./components/Loading";

function Root(props) {
	const navigation = useNavigation();
  return (
    <>
      <Outlet />
      {navigation.state != 'idle' && <Loading />}
    </>
  )
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    errorElement: <ErrorPage />,
    children: [
      {
        path: "/",
        element: <Home />,
        action: submitTask
      },
      {
        path: "/app/task/:taskId",
        element: <Task />,
        loader: taskLoader
      }
    ]
  }
]);

function App() {
  return (
    <RouterProvider router={router} />
  );
}

export default App
