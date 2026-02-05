import React from 'react';
import './App.css';

import { BrowserRouter, Switch, Route, Redirect } from "react-router-dom";
import Login from './components/login/Login';
import PaymentReport from './components/payment report/PaymentReport';
import PaymentsBasket from './components/payment report/PaymentsBasket';
import TransactionsReport from './components/transactions report/TransactionsReport';
import UploadCSVFile from "./components/upload cvs file/UploadCSVFile";
import StudentProfile from './components/student/StudentProfile';
import BankAccount from './components/bank account/BankAccount';
import ReceptionBasket from './components/reception basket/ReceptionBasket';
import PeriodicReception from './components/reception basket/PeriodicReception';
import StudentsBasket from './components/students basket/StudentsBasket';
import PeriodicStudents from './components/students basket/PeriodicStudents';
import StudentForm from "./components/student-form/StudentForm";

function App() {
  return (
    <BrowserRouter basename='/'>
      <Redirect to='/login' />
      {localStorage.getItem('remember') === 'true' && sessionStorage.setItem('login', 'true')}
      {!sessionStorage.getItem('route') && localStorage.getItem('remember') === 'true' && sessionStorage.setItem('route', '/finance-report')}
      {sessionStorage.getItem('login') && <Redirect to={`${sessionStorage.getItem('route') || '/login'}`} />}
      <Switch>
        <Route path='/import-data' component={UploadCSVFile} />

        <Route path='/bank-account' component={BankAccount} />

        <Route path='/transactions-report' component={TransactionsReport} />

        <Route path='/periodic-reception/reception-basket' component={ReceptionBasket} />
        <Route path='/periodic-reception' component={PeriodicReception} />

        <Route path='/students-reception/students-basket' component={StudentsBasket} />
        <Route path='/students-reception' component={PeriodicStudents} />

        <Route path='/finance-report/payments-basket' component={PaymentsBasket} />
        <Route path='/finance-report/student-profile' component={StudentProfile} />
        <Route path='/finance-report' component={PaymentReport} />

        <Route path='/student-form' component={StudentForm} />

        <Route path='/login' component={Login} />
      </Switch>
    </BrowserRouter>
  );
}

export default App;
