import loginStore from "./components/login/LoginStore";
import financeReportStore from './components/finance report/FinanceReportStore';
import paymentsBasketStore from './components/finance report/PaymentsBasketStore';
import periodicReceptionStore from './components/periodic reception/PeriodicReceptionStore';
import receptionBasketStore from './components/periodic reception/ReceptionBasketStore';
import transactionsReportStore from './components/transactions report/TransactionsReportStore';
import importDataStore from './components/import data/ImportDataStore';
import bankAccountStore from './components/bank account/BankAccountStore';

const Store = {
    loginStore,
    financeReportStore,
    paymentsBasketStore,
    periodicReceptionStore,
    receptionBasketStore,
    transactionsReportStore,
    importDataStore,
    bankAccountStore,
}

export default Store;