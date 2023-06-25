
import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Header from './components/Header/Header';
import { Loading } from './pages/Loading';
import { ResultTable } from './components/ResultTable/ResultTable';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Header />}>
          <Route path='' element={<Loading />} />
          <Route path='/result/:id' element={<ResultTable />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
