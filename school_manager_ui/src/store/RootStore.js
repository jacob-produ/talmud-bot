import loginStore from './LoginStore';
import paymentReportStore from './PaymentReportStore';
import paymentsBasketStore from './PaymentsBasketStore';
import transactionsReportStore from './TransactionsReportStore';
import studentStore from './StudentStore';
import uploadCSVFile from './UploadCSVFileStore';
import bankAccountStore from './BankAccountStore';
import receptionBasketStore from './ReceptionBasketStore';
import periodicReceptionStore from './PeriodicReceptionStore';

const RootStore = {
    loginStore,
    paymentReportStore,
    paymentsBasketStore,
    transactionsReportStore,
    studentStore,
    uploadCSVFile,
    bankAccountStore,
    receptionBasketStore,
    periodicReceptionStore
}
export default RootStore;