import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class UploadCSVFile {
    constructor() {
        makeAutoObservable(this);
    }

    loader = false;
    institutionBankAccount = null;
    branch = null;
    trendCoordinator = null;
    courseEnrollmentTrendCoordinatorAttribution = null;
    students = null;
    courseEnrollment = null;
    studentsIncomes = null;
    studentsIncomesSourceID = '';
    studentsIncomesMethod = '';
    studentsIncomesBankAccountNumber = '';
    studentsIncomesUpdate = false;
    institutionBankAccountUpdate = false;
    branchUpdate = false;
    trendCoordinatorUpdate = false;
    courseEnrollmentTrendCoordinatorAttributionUpdate = false;
    studentsUpdate = false;
    courseEnrollmentUpdate = false;
    supplierUpdate = false;
    donatorUpdate = false;
    generalBanksUpdate = false;
    periodicReceptionUpdate = false;
    clearingPlatformUpdate = false;
    msvScrapingPlatformUpdate = false;
    currentAccountUpdate = false;
    studentsPaymentFailureUpdate = false;
    clearingUpdate = false;
    clearingValidationUpdate = false;
    msvUpdate = false;
    checksUpdate = false;
    invoiceUpdate = false;
    studentInsuranceUpdate = false;
    expenseDraftFixedUpdate = false;
    studentsPaymentStatus = '';
    studentsPaymentFailure = null;
    currentAccount = null;
    currentAccountBankAccountNumber  = null;
    clearingPlatform = null;
    msvScrapingPlatform = null;
    clearingPlatformTrendCoordinatorID = '';
    msvScraping = '';
    clearing = null;
    clearingPlatformID = '';
    clearingValidation = null;
    msv = null;
    msvAttribution = '';
    msvBankAccountNumber = '';
    msvForDate = new Date().toISOString().slice(0, 10);
    msvTrendCoordinator = '';
    msvScrapingTrendCoordinator = '';
    msvSendingDate = new Date().toISOString().slice(0, 10);
    checks = null;
    checksAttribution = '';
    checksBankAccountNumber = '';
    generalBanks = null;
    generalBanksAttribution = '';
    supplier = null;
    invoice = null;
    invoiceInstitutionBranchCoordinator = '';
    invoiceTrendCoordinator = '';
    invoiceMsvScraping = '';
    invoiceSupplier = '';
    invoiceDate = new Date().toISOString().slice(0, 10);
    invoiceSum = '0';
    invoiceNumber = '';
    invoiceLastDate = '';
    studentInsurance = null;
    studentInsuranceBankAccountNumber = '';
    expenseDraft = null;
    expenseDraftAttribution = '';
    expenseDraftForMonth = new Date().toISOString().slice(0, 10);
    expenseDraftTrendCoordinator = '';
    expenseDraftBankAccountNumber = '';
    expenseDraftPaymentMethod = '';
    expenseDraftScholarshipType = '';
    expenseDraftFixed = false;
    donator = null;
    periodicReception = null;
    periodicReceptionBankAccountNumber = '';
    incomeSource = [];
    paymentMethods = [];
    attributions = [];
    paymentStatus = [];
    scholarshipTypes = [];
    bankAccounts = [];
    institutionBranchCoordinators = [];
    trendCoordinators = [];
    msvScrapingOptions = [];
    suppliers = [];
    platforms = [];
    errorInstitutionBankAccount = '';
    errorBranch = '';
    errorTrendCoordinator = '';
    errorCourseEnrollmentTrendCoordinatorAttribution = '';
    errorStudents = '';
    errorCourseEnrollment = '';
    errorStudentsIncomes = '';
    errorStudentsPaymentFailure = '';
    errorCurrentAccount = '';
    errorClearingPlatform = '';
    errorMsvScraping = '';
    errorClearing = '';
    errorMsvScrapingPlatform = '';
    errorClearingValidation = '';
    errorMSV = '';
    errorChecks = '';
    errorGeneralBanks = '';
    errorSupplier = ''
    errorInvoice = ''
    errorStudentInsurance = '';
    errorExpenseDraft = '';
    errorDonator = '';
    errorPeriodicReception = '';
    googleSheetsInstitutionBankAccount=false;
    googleSheetsBranch=false;
    googleSheetsTrendCoordinator=false;
    googleSheetsCourseEnrollmentTrendCoordinatorAttribution=false;
    googleSheetsStudents=false;
    googleSheetsCourseEnrollment=false;
    googleSheetsSupplier=false;
    googleSheetsDonator=false;
    googleSheetsGeneralBanks=false;
    googleSheetsPeriodicReception=false;
    googleSheetsClearingPlatform=false;
    googleSheetsMsvScrapingPlatform=false;
    googleSheetsCurrentAccount=false;
    googleSheetsStudentsIncomes=false;
    googleSheetsStudentsPaymentFailure=false;
    googleSheetsClearing=false;
    googleSheetsClearingValidation=false;
    googleSheetsMSV=false;
    googleSheetsChecks=false;
    googleSheetsInvoice=false;
    googleSheetsStudentInsurance=false;
    googleSheetsExpenseDraft=false;

    setErrorInstitutionBankAccount = (value) => {
        this.errorInstitutionBankAccount = value;
    }

    setErrorBranch = (value) => {
        this.errorBranch = value;
    }

    setErrorTrendCoordinator = (value) => {
        this.errorTrendCoordinator = value;
    }

    setErrorCourseEnrollmentTrendCoordinatorAttribution = (value) => {
        this.errorCourseEnrollmentTrendCoordinatorAttribution = value;
    }

    setErrorStudents = (value) => {
        this.errorStudents = value;
    }

    setErrorCourseEnrollment = (value) => {
        this.errorCourseEnrollment = value;
    }

    setErrorStudentsIncomes = (value) => {
        this.errorStudentsIncomes = value;
    }

    setErrorStudentsPaymentFailure = (value) => {
        this.errorStudentsPaymentFailure = value;
    }

    setErrorCurrentAccount = (value) => {
        this.errorCurrentAccount = value;
    }

    setErrorClearingPlatform = (value) => {
        this.errorclearingPlatform = value;
    }
    setErrorMsvScrapingPlatform = (value) => {
        this.errorMsvScrapingPlatform = value;
    }

    setErrorClearing = (value) => {
        this.errorClearing = value;
    }

    setErrorClearingValidation = (value) => {
        this.errorClearingValidation = value;
    }

    setErrorMSV = (value) => {
        this.errorMSV = value;
    }

    setErrorChecks = (value) => {
        this.errorChecks = value;
    }

    setErrorGeneralBanks = (value) => {
        this.errorGeneralBanks = value;
    }

    setErrorSupplier = (value) => {
        this.errorSupplier = value;
    }

    setErrorInvoice = (value) => {
        this.errorInvoice = value;
    }

    setErrorStudentInsurance = (value) => {
        this.errorStudentInsurance = value;
    }

    setErrorExpenseDraft = (value) => {
        this.errorExpenseDraft = value;
    }

    setErrorDonator = (value) => {
        this.errorDonator = value;
    }

    setErrorPeriodicReception = (value) => {
        this.errorPeriodicReception = value;
    }

    setPeriodicReception = (file) => {
        this.periodicReception = file;
        this.setErrorPeriodicReception('');
    }

    setGoogleSheetsPeriodicReception = (value) => {
        this.googleSheetsDonator = value;
    }
    setPeriodicReceptionBankAccountNumber = (value) => {
        this.periodicReceptionBankAccountNumber = value;
    }

    setDonator = (file) => {
        this.donator = file;
        this.setErrorDonator('');
    }
    setGoogleSheetsDonator = (value) => {
        this.googleSheetsDonator = value;
    }

    setExpenseDraft = (file) => {
        this.expenseDraft = file;
        this.setErrorExpenseDraft('');
    }

    setGoogleSheetsExpenseDraft = (value) => {
        this.googleSheetsExpenseDraft = value;
    }
    setExpenseDraftAttribution = (value) => {
        this.expenseDraftAttribution = value;
    }

    setExpenseDraftForMonth = (value) => {
        this.expenseDraftForMonth = value;
    }

    setExpenseDraftTrendCoordinator = (value) => {
        this.expenseDraftTrendCoordinator = value;
    }

    setExpenseDraftBankAccountNumber = (value) => {
        this.expenseDraftBankAccountNumber = value;
    }

    setExpenseDraftPaymentMethod = (value) => {
        this.expenseDraftPaymentMethod = value;
    }

    setExpenseDraftScholarshipType = (value) => {
        this.expenseDraftScholarshipType = value;
    }

    setExpenseDraftFixed = (checked) => {
        this.expenseDraftFixed = checked;
    }

    setStudentInsurance = (file) => {
        this.studentInsurance = file;
        this.setErrorStudentInsurance('');
    }

    setGoogleSheetsStudentInsurance = (value) => {
        this.googleSheetsStudentInsurance = value;
    }
    setStudentInsuranceBankAccountNumber = (value) => {
        this.studentInsuranceBankAccountNumber = value;
    }

    setInvoice = (file) => {
        this.invoice = file;
        this.setErrorSupplier('');
    }

    setGoogleSheetsInvoice = (value) => {
        this.googleSheetsInvoice = value;
    }
    setInvoiceInstitutionBranchCoordinator = (value) => {
        this.invoiceInstitutionBranchCoordinator = value;
    }

    setInvoiceTrendCoordinator = (value) => {
        this.invoiceTrendCoordinator = value;
    }
    setInvoiceMsvScraping = (value) => {
        this.invoiceMsvScraping = value;
    }

    setInvoiceSupplier = (value) => {
        this.invoiceSupplier = value;
    }

    setInvoiceDate = (value) => {
        this.invoiceDate = value;
    }

    setInvoiceSum = (value) => {
        this.invoiceSum = value || '0';
    }

    setInvoiceNumber = (value) => {
        this.invoiceNumber = value;
    }

    setInvoiceLastDate = (value) => {
        this.invoiceLastDate = value;
    }

    setSupplier = (file) => {
        this.supplier = file;
        this.setErrorSupplier('');
    }

    setGeneralBanks = (file) => {
        this.generalBanks = file;
        this.setErrorGeneralBanks('');
    }
    setGoogleSheetsGeneralBanks = (value) => {
        this.googleSheetsGeneralBanks = value;
    }

    setGeneralBanksAttribution = (value) => {
        this.generalBanksAttribution = value;
    }

    setChecks = (file) => {
        this.checks = file;
        this.setErrorChecks('');
    }

    setGoogleSheetsChecks = (value) => {
        this.googleSheetsChecks = value;
    }
    setChecksAttribution = (value) => {
        this.checksAttribution = value;
    }

    setChecksBankAccountNumber = (value) => {
        this.checksBankAccountNumber = value;
    }

    setMSV = (file) => {
        this.msv = file;
        this.setErrorMSV('');
    }

    setGoogleSheetsMSV = (value) => {
        this.googleSheetsMSV = value;
    }
    setMsvAttribution = (value) => {
        this.msvAttribution = value;
    }

    setMsvBankAccountNumber = (value) => {
        this.msvBankAccountNumber = value;
    }

    setMsvForDate = (date) => {
        this.msvForDate = date;
    }

    setMsvTrendCoordinator = (value) => {
        this.msvTrendCoordinator = value;
    }
    setMsvScrapingTrendCoordinator = (value) => {
        this.msvScrapingTrendCoordinator = value;
    }

    setMsvSendingDate = (date) => {
        this.msvSendingDate = date;
    }

    setClearingPlatform = (file) => {
        this.clearingPlatform = file;
        this.setErrorClearingPlatform('');
    }
    setMsvScrapingPlatform = (file) => {
        this.msvScrapingPlatform = file;
        this.setErrorMsvScrapingPlatform('');
    }
    setGoogleSheetsClearingPlatform = (value) => {
        this.googleSheetsClearingPlatform = value;
    }
    setGoogleSheetsMsvScrapingPlatform = (value) => {
        this.googleSheetsMsvScrapingPlatform = value;
    }

    setClearingValidation = (file) => {
        this.clearingValidation = file;
        this.setErrorClearingValidation('');
    }

    setGoogleSheetsClearingValidation = (value) => {
        this.googleSheetsClearingValidation = value;
    }
    setClearingPlatformTrendCoordinatorID = (value) => {
        this.clearingPlatformTrendCoordinatorID = value;
    }
    setMsvScraping = (value) => {
        this.msvScraping = value;
    }

    setClearing = (file) => {
        this.clearing = file;
        this.setErrorClearing('');
    }
    setGoogleSheetsClearing = (value) => {
        this.googleSheetsClearing = value;
    }

    setClearingPlatformID = (value) => {
        this.clearingPlatformID = value;
    }

    setAttributions = (value) => {
        this.attributions = value;
        if (value) {
            const firstAttribution = value[0];
            this.setMsvAttribution(firstAttribution);
            this.setChecksAttribution(firstAttribution);
            this.setGeneralBanksAttribution(firstAttribution);
            this.setExpenseDraftAttribution(firstAttribution);
        }
    }

    setBankAccounts = (value) => {
        this.bankAccounts = value;
        if (value.length > 0) {
            const firstBankAccountNumber = value[0].account_number;
            this.setMsvBankAccountNumber(firstBankAccountNumber);
            this.setChecksBankAccountNumber(firstBankAccountNumber);
            this.setStudentsIncomesBankAccountNumber(firstBankAccountNumber);
            this.setStudentInsuranceBankAccountNumber(firstBankAccountNumber);
            this.setExpenseDraftBankAccountNumber(firstBankAccountNumber)
            this.setPeriodicReceptionBankAccountNumber(firstBankAccountNumber);
            this.setCurrentAccountBankAccountNumber(firstBankAccountNumber)
        }
    }

    setIncomeSource = (value) => {
        this.incomeSource = value;
        value.length > 0 && this.setStudentsIncomesSourceID(value[0].id);
    }

    setPaymentMethods = (value) => {
        this.paymentMethods = value;
        value.length > 0 && this.setStudentsIncomesMethod(value[0]);
    }

    setPaymentStatus = (value) => {
        this.paymentStatus = value
        value.length > 0 && this.setStudentsPaymentStatus(value[0]);
    }

    setScholarshipTypes = (value) => {
        this.scholarshipTypes = value;
        value.length > 0 && this.setExpenseDraftScholarshipType(value[0])
    }

    setInstitutionBranchCoordinators = (value) => {
        const objValue = Object.values(value);
        this.institutionBranchCoordinators = objValue;
        objValue.length > 0 && this.setInvoiceInstitutionBranchCoordinator(objValue[0].identity)
    }

    setTrendCoordinators = (value) => {
        this.trendCoordinators = value;
        value.length > 0 && this.setInvoiceTrendCoordinator(value[0].name);
        value.length > 0 && this.setMsvTrendCoordinator(value[0].id);
    }
    setMsvScrapingOptions = (value) => {
        this.msvScrapingOptions = value;
        value.length > 0 && this.setInvoiceMsvScraping(value[0].name);
        value.length > 0 && this.setMsvScrapingTrendCoordinator(value[0].id);
    }

    setSuppliers = (value) => {
        this.suppliers = value;
        value.length > 0 && this.setInvoiceSupplier(value[0].identity);
    }
    setGoogleSheetsSupplier = (value) => {
        this.googleSheetsSupplier = value;
    }
    
    setPlatforms = (value) => {
        this.platforms = value;
        value.length > 0 && this.setClearingPlatformID(value[0].id);
    }

    setLoader = (value) => {
        this.loader = value;
    }

    setInstitutionBankAccount = (value) => {
        this.institutionBankAccount = value;
        this.setErrorInstitutionBankAccount('');
    }
    setGoogleSheetsInstitutionBankAccount = (value) => {
        console.log(value);
        this.googleSheetsInstitutionBankAccount = value;
    }
    
    setBranch = (value) => {
        this.branch = value;
        this.setErrorBranch('');
    }
    setGoogleSheetsBranch = (value) => {
        this.googleSheetsBranch = value;
    }
    
    setTrendCoordinator = (value) => {
        this.trendCoordinator = value;
        this.setErrorTrendCoordinator('');
    }
    setGoogleSheetsTrendCoordinator = (value) => {
        this.googleSheetsTrendCoordinator = value;
    }
    
    setCourseEnrollmentTrendCoordinatorAttribution = (value) => {
        this.courseEnrollmentTrendCoordinatorAttribution = value;
        this.setErrorCourseEnrollmentTrendCoordinatorAttribution('');
    }
    setGoogleSheetsCourseEnrollmentTrendCoordinatorAttribution = (value) => {
        this.googleSheetsCourseEnrollmentTrendCoordinatorAttribution = value;
    }
    
    setStudents = (value) => {
        this.students = value;
        this.setErrorStudents('');
    }
    setGoogleSheetsStudents = (value) => {
        this.googleSheetsStudents = value;
    }
    
    setCourseEnrollment = (value) => {
        this.courseEnrollment = value;
        this.setErrorCourseEnrollment('');
    }
    
    setGoogleSheetsCourseEnrollment = (value) => {
        this.googleSheetsCourseEnrollment = value;
    }
    setStudentsIncomes = (value) => {
        this.studentsIncomes = value;
        this.setErrorStudentsIncomes('');
    }
    setGoogleSheetsStudentsIncomes = (value) => {
        this.googleSheetsStudentsIncomes = value;
    }

    setStudentsPaymentFailure = (value) => {
        this.studentsPaymentFailure = value;
        this.setErrorStudentsPaymentFailure('');
    }
    setGoogleSheetsStudentsPaymentFailure = (value) => {
        this.googleSheetsStudentsPaymentFailure = value;
    }

    setStudentsIncomesSourceID = (value) => {
        this.studentsIncomesSourceID = value;
    }

    setStudentsIncomesMethod = (value) => {
        this.studentsIncomesMethod = value;
    }

    setStudentsIncomesBankAccountNumber = (value) => {
        this.studentsIncomesBankAccountNumber = value;
    }

    setStudentsIncomesUpdate = (value) => {
        this.studentsIncomesUpdate = value;
    }

    setInstitutionBankAccountUpdate = (value) => {
        this.institutionBankAccountUpdate = value;
    }
    setBranchUpdate = (value) => {
        this.branchUpdate = value;
    }
    setTrendCoordinatorUpdate = (value) => {
        this.trendCoordinatorUpdate = value;
    }
    setCourseEnrollmentTrendCoordinatorAttributionUpdate = (value) => {
        this.courseEnrollmentTrendCoordinatorAttributionUpdate = value;
    }
    setStudentsUpdate = (value) => {
        this.studentsUpdate = value;
    }
    setCourseEnrollmentUpdate = (value) => {
        this.courseEnrollmentUpdate = value;
    }
    setSupplierUpdate = (value) => {
        this.supplierUpdate = value;
    }
    setDonatorUpdate = (value) => {
        this.donatorUpdate = value;
    }
    setGeneralBanksUpdate = (value) => {
        this.generalBanksUpdate = value;
    }
    setPeriodicReceptionUpdate = (value) => {
        this.periodicReceptionUpdate = value;
    }
    setMsvScrapingPlatformUpdate = (value) => {
        this.msvScrapingPlatformUpdate = value;
    }
    setClearingPlatformUpdate = (value) => {
        this.clearingPlatformUpdate = value;
    }
    setCurrentAccountUpdate = (value) => {
        this.currentAccountUpdate = value;
    }
    setStudentsPaymentFailureUpdate = (value) => {
        this.studentsPaymentFailureUpdate = value;
    }
    setClearingUpdate = (value) => {
        this.clearingUpdate = value;
    }
    setClearingValidationUpdate = (value) => {
        this.clearingValidationUpdate = value;
    }
    setMsvUpdate = (value) => {
        this.msvUpdate = value;
    }
    setChecksUpdate = (value) => {
        this.checksUpdate = value;
    }
    setInvoiceUpdate = (value) => {
        this.invoiceUpdate = value;
    }
    setStudentsInsuranceUpdate = (value) => {
        this.studentInsuranceUpdate = value;
    }
    setExpenseDraftFixedUpdate = (value) => {
        this.expenseDraftFixedUpdate = value;
    }



    setStudentsPaymentStatus = (value) => {
        this.studentsPaymentStatus = value;
    }

    setCurrentAccount = (value) => {
        this.currentAccount = value;
        this.setErrorCurrentAccount('');
    }
    setGoogleSheetsCurrentAccount = (value) => {
        this.googleSheetsCurrentAccount = value;
    }
    setCurrentAccountBankAccountNumber = (value) => {
        this.currentAccountBankAccountNumber = value;
    }

    sendData = async () => {
        const fetch_1 = this.fetchInstitutionBankAccount();
        const fetch_2 = this.fetchBranch();
        const fetch_3 = this.fetchTrendCoordinator();
        const fetch_4 = this.fetchCourseEnrollmentTrendCoordinatorAttribution();
        const fetch_5 = this.fetchStudents();
        const fetch_6 = this.fetchCourseEnrollment();
        const fetch_7 = this.fetchStudentsIncomes();
        const fetch_8 = this.fetchStudentsPaymentFailure();
        const fetch_9 = this.fetchCurrentAccount();
        const fetch_10 = this.fetchClearingPlatform();
        const fetch_11 = this.fetchClearing();
        const fetch_12 = this.fetchClearingValidation();
        const fetch_13 = this.fetchMSV();
        const fetch_14 = this.fetchChecks();
        const fetch_15 = this.fetchGeneralBanks();
        const fetch_16 = this.fetchSupplier();
        const fetch_17 = this.fetchInvoice();
        const fetch_18 = this.fetchStudentInsurance();
        const fetch_19 = this.fetchExpenseDraft();
        const fetch_20 = this.fetchDonator();
        const fetch_21 = this.fetchPeriodicReception();
        const fetch_22 = this.fetchMsvScraping();

        return await Promise.all([fetch_1, fetch_2, fetch_3, fetch_4, fetch_5, fetch_6, fetch_7, fetch_8, fetch_9, fetch_10,
            fetch_11, fetch_12, fetch_13, fetch_14, fetch_15, fetch_16, fetch_17, fetch_18, fetch_19, fetch_20, fetch_21,fetch_22])
            .then((res) => {
                this.setLoader(false);
                return res;
            })
            .catch(err => console.error(err))
    }

    fetchInstitutionBankAccount = async () => {
        this.setErrorInstitutionBankAccount('');
        if (this.institutionBankAccount || this.googleSheetsInstitutionBankAccount) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('institution_bank_account_csv', this.institutionBankAccount);
            formData.append('google_sheets', this.googleSheetsInstitutionBankAccount);
            return await (this.institutionBankAccountUpdate ? Fetch.PutFormData : Fetch.PostFormData)('institution_bank_account', formData)
                .then(res => {
                    res.error ? this.setErrorInstitutionBankAccount(res.message.value || res.message) : this.setInstitutionBankAccount(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchBranch = async () => {
        this.setErrorBranch('');
        if (this.branch || this.googleSheetsBranch) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('branch_csv', this.branch);
            formData.append('google_sheets', this.googleSheetsBranch);

            return await (this.branchUpdate ? Fetch.PutFormData : Fetch.PostFormData)('branch', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorBranch(res.message.value || res.message) : this.setBranch(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchTrendCoordinator = async () => {
        this.setErrorTrendCoordinator('');
        if (this.trendCoordinator || this.googleSheetsTrendCoordinator) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('trend_coordinator_csv', this.trendCoordinator);
            formData.append('google_sheets', this.googleSheetsTrendCoordinator);

            return await (this.trendCoordinatorUpdate ? Fetch.PutFormData : Fetch.PostFormData)('trend_coordinator', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorTrendCoordinator(res.message.value || res.message) : this.setTrendCoordinator(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchCourseEnrollmentTrendCoordinatorAttribution = async () => {
        this.setErrorCourseEnrollmentTrendCoordinatorAttribution('');
        if (this.courseEnrollmentTrendCoordinatorAttribution || this.googleSheetsCourseEnrollmentTrendCoordinatorAttribution) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('course_enrollment_trend_coordinator_attribution_csv', this.courseEnrollmentTrendCoordinatorAttribution);
            formData.append('google_sheets', this.googleSheetsCourseEnrollmentTrendCoordinatorAttribution);
            return await (this.courseEnrollmentTrendCoordinatorAttributionUpdate ? Fetch.PutFormData : Fetch.PostFormData)('course_enrollment_trend_coordinator_attribution', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorCourseEnrollmentTrendCoordinatorAttribution(res.message.value || res.message) : this.setCourseEnrollmentTrendCoordinatorAttribution(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchStudents = async () => {
        this.setErrorStudents('');
        if (this.students || this.googleSheetsStudents) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('students_csv', this.students);
            formData.append('google_sheets', this.googleSheetsStudents);

            return await (this.studentsUpdate ? Fetch.PutFormData : Fetch.PostFormData)('student', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorStudents(res.message.value || res.message) : this.setStudents(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchCourseEnrollment = async () => {
        this.setErrorCourseEnrollment('');
        if (this.courseEnrollment || this.googleSheetsCourseEnrollment) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('course_enrollment_csv', this.courseEnrollment);
            formData.append('google_sheets', this.courseEnrollment);
            return await (this.courseEnrollmentUpdate ? Fetch.PutFormData : Fetch.PostFormData)('course_enrollment', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorCourseEnrollment(res.message.value || res.message) : this.setCourseEnrollment(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchStudentsIncomes = async () => {
        this.setErrorStudentsIncomes('');
        if (this.studentsIncomes || this.googleSheetsStudentsIncomes) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('students_incomes_csv', this.studentsIncomes);
            formData.append('fk_income_source_id', this.studentsIncomesSourceID);
            formData.append('method', this.studentsIncomesMethod);
            formData.append('account_number', this.studentsIncomesBankAccountNumber);
            formData.append('payment_status', this.studentsPaymentStatus);
            formData.append('google_sheets', this.googleSheetsStudentsIncomes);

            return await (this.studentsIncomesUpdate ? Fetch.PutFormData : Fetch.PostFormData)('income', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorStudentsIncomes(res.message.value || res.message) : this.setStudentsIncomes(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchStudentsPaymentFailure = async () => {
        this.setErrorStudentsPaymentFailure('');
        if (this.studentsPaymentFailure || this.googleSheetsStudentsPaymentFailure) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('payment_failure_csv', this.studentsPaymentFailure);
            formData.append('google_sheets', this.googleSheetsStudentsPaymentFailure);

            return await (this.studentsPaymentFailureUpdate ? Fetch.PutFormData : Fetch.PostFormData)('payment_failure', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorStudentsPaymentFailure(res.message.value || res.message) : this.setStudentsPaymentFailure(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchCurrentAccount = async () => {
        this.setErrorCurrentAccount('');
        if (this.currentAccount || this.googleSheetsCurrentAccount) {
            this.setLoader(true);

            const formData = new FormData();
            formData.append('current_account_csv', this.currentAccount);
            if(this.currentAccountBankAccountNumber){
                formData.append('account_number ', this.currentAccountBankAccountNumber);
            }
            formData.append('google_sheets', this.googleSheetsCurrentAccount);

            return await (this.currentAccountUpdate ? Fetch.PutFormData : Fetch.PostFormData)('current_account', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorCurrentAccount(res.message.value || res.message) : this.setCurrentAccount(null) ;
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchClearingPlatform = async () => {
        this.setErrorClearingPlatform('');
        if (this.clearingPlatform || this.googleSheetsClearingPlatform) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('clearing_platform_csv', this.clearingPlatform);
            formData.append('google_sheets', this.googleSheetsClearingPlatform);
            this.clearingPlatformTrendCoordinatorID !== '' && formData.append('trend_coordinator_id', this.clearingPlatformTrendCoordinatorID);
            return await (this.clearingPlatformUpdate ? Fetch.PutFormData : Fetch.PostFormData)('clearing_platform', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorClearingPlatform(res.message.value || res.message) : this.setClearingPlatform(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchClearing = async () => {
        this.setErrorClearing('');
        if (this.clearing || this.googleSheetsClearing) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('clearing_payments_csv', this.clearing);
            formData.append('fk_platform_id', this.clearingPlatformID);
            formData.append('google_sheets', this.googleSheetsClearing);
            return await (this.clearingUpdate ? Fetch.PutFormData : Fetch.PostFormData)('clearing', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorClearing(res.message.value || res.message) : this.setClearing(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }
    fetchMsvScraping = async () => {
        this.setErrorMsvScrapingPlatform('');
        if (this.msvScrapingPlatform || this.googleSheetsMsvScrapingPlatform) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('msv_scraping_csv', this.msvScrapingPlatform);
            formData.append('google_sheets', this.googleSheetsMsvScrapingPlatform);
            this.msvScraping !== '' && formData.append('msv_scraping_csv', this.msvScraping);
            return await (this.msvScrapingPlatformUpdate ? Fetch.PutFormData : Fetch.PostFormData)('msv_scraping', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorMsvScrapingPlatform(res.message.value || res.message) : this.setMsvScrapingPlatform(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }


    fetchClearingValidation = async () => {
        this.setErrorClearingValidation('');
        if (this.clearingValidation || this.googleSheetsClearingValidation) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('clearing_validation_csv', this.clearingValidation);
            formData.append('google_sheets', this.googleSheetsClearingValidation);
            return await (this.clearingValidationUpdate ? Fetch.PutFormData : Fetch.PostFormData)('clearing_validation', formData)
                .then(res => {
                    console.log(res);
                    res.error ? this.setErrorClearingValidation(res.message.value || res.message) : this.setClearingValidation(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchMSV = async () => {
        this.setErrorMSV('');
        if (this.msv || this.googleSheetsMSV) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('msv_expense_csv', this.msv);
            formData.append('attribution', this.msvAttribution);
            formData.append('account_number', this.msvBankAccountNumber);
            formData.append('for_month', this.msvForDate.split('-').reverse().join('/'));
            formData.append('fk_trend_coordinator_id', this.msvTrendCoordinator);
            formData.append('msv_sending_date', this.msvSendingDate.split('-').reverse().join('/'));
            formData.append('google_sheets', this.googleSheetsMSV);
            return await (this.msvUpdate ? Fetch.PutFormData : Fetch.PostFormData)('msv', formData)
                .then(res => {
                    console.log(res);
                    res?.inserted_records?.error ? this.setErrorMSV(res.inserted_records.message.value || res.message) : this.setMSV(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchChecks = async () => {
        this.setErrorChecks('');
        if (this.checks || this.googleSheetsChecks) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('check_expense_csv', this.checks);
            formData.append('attribution', this.checksAttribution);
            formData.append('account_number', this.checksBankAccountNumber);
            formData.append('google_sheets', this.googleSheetsChecks);

            return await (this.checksUpdate ? Fetch.PutFormData : Fetch.PostFormData)('check', formData)
                .then(res => {
                    console.log(res);
                    res?.inserted_records?.error ? this.setErrorChecks(res.inserted_records.message.value || res.message) : this.setChecks(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchGeneralBanks = async () => {
        this.setErrorGeneralBanks('');
        if (this.generalBanks || this.googleSheetsGeneralBanks) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('general_bank_account_csv', this.generalBanks);
            formData.append('attribution', this.generalBanksAttribution);
            formData.append('google_sheets', this.googleSheetsGeneralBanks);

            return await (this.generalBanksUpdate ? Fetch.PutFormData : Fetch.PostFormData)('general_bank_account', formData)
                .then(res => {
                    console.log(res);
                    res?.inserted_records?.error ? this.setErrorGeneralBanks(res.inserted_records.message.value || res.message) : this.setGeneralBanks(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchSupplier = async () => {
        this.setErrorSupplier('');
        if (this.supplier || this.googleSheetsSupplier) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('supplier_csv', this.supplier);
            formData.append('google_sheets', this.googleSheetsSupplier);

            return await (this.supplierUpdate ? Fetch.PutFormData : Fetch.PostFormData)('supplier', formData)
                .then(res => {
                    console.log(res);
                    res?.error ? this.setErrorSupplier(res.message.value || res.message) : this.setSupplier(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchInvoice = async () => {
        this.setErrorInvoice('');
        if (this.invoice) {
            if (this.invoiceNumber || this.googleSheetsInvoice) {
                this.setLoader(true);
                const formData = new FormData();
                formData.append('invoice_file', this.invoice);
                formData.append('institution_identity', this.invoiceInstitutionBranchCoordinator.identity);
                formData.append('trend_coordinator_name', this.invoiceTrendCoordinator.name);
                formData.append('supplier_identity', this.invoiceSupplier.identity);
                formData.append('invoice_date', `${this.invoiceDate}T00:00:00`);
                formData.append('invoice_number', this.invoiceNumber);
                formData.append('amount', this.invoiceSum);
                formData.append('google_sheets', this.googleSheetsInvoice);

                this.invoiceLastDate.trim() !== '' && formData.append('payment_due_date', `${this.invoiceLastDate}T00:00:00`);
                return await (this.invoiceUpdate ? Fetch.PutFormData : Fetch.PostFormData)('invoice', formData)
                    .then(res => {
                        console.log(res);
                        res?.error ? this.setErrorInvoice(res.message.payment_due_date[0] || res.message) : this.setInvoice(null);
                        return res;
                    })
                    .catch(err => console.error(err))
            }
            else {
                this.setErrorInvoice('חסר מספר חשבונית');
            }
        }
    }

    fetchStudentInsurance = async () => {
        this.setErrorStudentInsurance('');
        if (this.studentInsurance || this.googleSheetsStudentInsurance) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('student_insurance_expense_csv', this.studentInsurance);
            formData.append('account_number', this.studentInsuranceBankAccountNumber);
            formData.append('google_sheets', this.googleSheetsStudentInsurance);
            return await (this.studentInsuranceUpdate ? Fetch.PutFormData : Fetch.PostFormData)('student_insurance', formData)
                .then(res => {
                    console.log(res);
                    res?.inserted_records?.error ? this.setErrorStudentInsurance(res.inserted_records.message.value || res.message) : this.setStudentInsurance(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchExpenseDraft = async () => {
        this.setErrorExpenseDraft('');
        if (this.expenseDraft || this.googleSheetsExpenseDraft) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('expense_draft_csv', this.expenseDraft);
            formData.append('attribution', this.expenseDraftAttribution);
            formData.append('account_number', this.expenseDraftBankAccountNumber);
            formData.append('for_month', this.expenseDraftForMonth.split('-').reverse().join('/'));
            formData.append('scholarship_type', this.expenseDraftAttribution === 'student' ? this.expenseDraftScholarshipType : null);
            formData.append('fixed', this.expenseDraftFixed);
            formData.append('google_sheets', this.googleSheetsExpenseDraft);

            this.expenseDraftPaymentMethod !== '' && formData.append('payment_method', this.expenseDraftPaymentMethod);
            this.expenseDraftTrendCoordinator !== '' && formData.append('fk_trend_coordinator_id', this.expenseDraftTrendCoordinator);
            return await (this.expenseDraftFixedUpdate ? Fetch.PutFormData : Fetch.PostFormData)('expense_draft', formData)
                .then(res => {
                    console.log(res);
                    res?.inserted_records?.error ? this.setErrorExpenseDraft(res.inserted_records.message.value || res.message) : this.setExpenseDraft(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchDonator = async () => {
        this.setErrorDonator('');
        if (this.donator || this.googleSheetsDonator) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('donator_csv', this.donator);
            formData.append('google_sheets', this.googleSheetsDonator);
            return await (this.donatorUpdate ? Fetch.PutFormData : Fetch.PostFormData)('donator', formData)
                .then(res => {
                    console.log(res);
                    res?.inserted_records?.error ? this.setErrorDonator(res.inserted_records.message.value || res.message) : this.setDonator(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchPeriodicReception = async () => {
        this.setErrorPeriodicReception('');
        if (this.periodicReception || this.googleSheetsPeriodicReception) {
            this.setLoader(true);
            const formData = new FormData();
            formData.append('periodic_reception_csv', this.periodicReception);
            formData.append('account_number', this.periodicReceptionBankAccountNumber);
            formData.append('google_sheets', this.googleSheetsPeriodicReception);
            return await (this.periodicReceptionUpdate ? Fetch.PutFormData : Fetch.PostFormData)('periodic_reception', formData)
                .then(res => {
                    console.log(res);
                    res?.inserted_records?.error ? this.setErrorPeriodicReception(res.inserted_records.message.value || res.message) : this.setPeriodicReception(null);
                    return res;
                })
                .catch(err => console.error(err))
        }
    }

    fetchIncomeSource = () => {
        Fetch.Get('income_source')
            .then(res => this.setIncomeSource(res))
            .catch(err => console.error(err))
    }

    fetchPaymentMethods = () => {
        Fetch.Get('general_lists')
            .then(res => {
                if (res) {
                    res.income_payment_methods && this.setPaymentMethods(res.income_payment_methods);
                    res.attributions && this.setAttributions(res.attributions);
                    res.education_payment_status && this.setPaymentStatus(res.education_payment_status);
                    res.scholarship_types && this.setScholarshipTypes(res.scholarship_types);
                }
            })
            .catch(err => console.error(err))
    }

    fetchBankAccounts = () => {
        Fetch.Get('bank_account?verbose=true')
            .then(res => this.setBankAccounts(res))
            .catch(err => console.error(err))
    }

    fetchInstitutionBranchCoordinators = () => {
        Fetch.Get('institution_branch_coordinator')
            .then(res => this.setInstitutionBranchCoordinators(res))
            .catch(err => console.error(err))
    }

    fetchTrendCoordinators = () => {
        Fetch.Get('trend_coordinator')
            .then(res => {
                this.setTrendCoordinators(res);
            })
            .catch(err => console.error(err))
    }

    fetchSuppliers = () => {
        Fetch.Get('supplier')
            .then(res => this.setSuppliers(res))
            .catch(err => console.error(err))
    }

    fetchPlatforms = () => {
        Fetch.Get('clearing_platform')
            .then(res => this.setPlatforms(res))
            .catch(err => console.error(err))
    }

    callFetch = () => {
        this.fetchIncomeSource();
        this.fetchPaymentMethods();
        this.fetchBankAccounts();
        this.fetchInstitutionBranchCoordinators();
        this.fetchTrendCoordinators();
        this.fetchSuppliers();
        this.fetchPlatforms();
    }

    fetchDownloadTemplate = async (template_from) => {
        return await Fetch.GetHeader(`${template_from}/csv_template`)
            .catch(err => console.error(err))
    }
}

export default new UploadCSVFile();