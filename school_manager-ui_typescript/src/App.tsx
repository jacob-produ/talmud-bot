import React, { useEffect } from 'react';
import './scss/style.scss';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from './components/login/Login';
import FinanceReport from './components/finance report/FinanceReport';
import PaymentsBasket from './components/finance report/payments basket/PaymentsBasket';
import PeriodicReception from './components/periodic reception/PeriodicReception';
import ReceptionBasket from './components/periodic reception/reception basket/ReceptionBasket';
import TransactionsReport from './components/transactions report/TransactionsReport';
import ImportData from './components/import data/ImportData';
import BankAccount from './components/bank account/BankAccount';

const App = () => {
  useEffect(() => {
    localStorage.getItem('remember') === 'true' && sessionStorage.setItem('login', 'true');
    !sessionStorage.getItem('route') && localStorage.getItem('remember') === 'true' && sessionStorage.setItem('route', '/finance-report')
  }, [])

  return (
    <BrowserRouter basename='/'>
      <Routes>
        <Route path='/bank-account' element={<BankAccount />} />

        <Route path='/import-data' element={<ImportData />} />

        <Route path='/transactions-report' element={<TransactionsReport />} />

        <Route path='/periodic-reception/reception-basket' element={<ReceptionBasket />} />
        <Route path='/periodic-reception' element={<PeriodicReception />} />

        <Route path='/finance-report/payments-basket' element={<PaymentsBasket />} />
        <Route path='/finance-report' element={<FinanceReport />} />

        <Route path='/login' element={<Login />} />
        <Route path="/" element={<Navigate replace to="/login" />} />
        <Route path="*" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

