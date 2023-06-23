import { useEffect, useState } from 'react'
import axios from 'axios';

import './App.css'
import { basePath } from './providers/env';
import { theme } from 'antd';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Header from './components/Header/Header';

function App() {
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    setMessage('Hello, world!');
    axios.get<{ msg: string }>(
      `${basePath}/api/v1/rating`).then(({ data }) => {
        setMessage(data.msg);
      })
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Header />}>
          {/* <Route path='' element={<Dashboard />} /> */}
          <Route path='' element={<h1>{message}</h1>} />
          {/* <Route path='/inn/:inn' element={<InnDetail />} /> */}
          <Route path="1" element={<h1 className="m-10">
            Hello world 1!
          </h1>} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
