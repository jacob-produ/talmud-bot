import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class StudentStore {
    constructor() {
        makeAutoObservable(this);
    }

    newStudentDetails = {};
    studentDetails = null;
    studentBalanceDetails = null;
    branchDetails = null;
    coordinatorDetails = null;
    tableData = null;
    editStudent = false;
    institutionBranchCoordinator = null;
    trendCoordinator = null
    generalLists = null;
    allInstitution = null;
    postBank = false;
    selectedTableTab = 'payments';

    setAllInstitution = (value) => {
        this.allInstitution = value;
    }

    setGeneralLists = (value) => {
        this.generalLists = value;
    }

    setTrendCoordinator = (value) => {
        this.trendCoordinator = value;
    }

    setInstitutionBranchCoordinator = (value) => {
        this.institutionBranchCoordinator = value;
    }

    changeSelectedData = (target, param, value, changeAll, index) => {
        const newTarget = target === 'student' ? this.studentDetails : target === 'branch' ? this.branchDetails :
            target === 'coordinator' ? this.coordinatorDetails : null;

        if (newTarget) {
            this.setEditStudent(true);
            if (changeAll) {
                if (target === 'student') {
                    this.studentDetails = changeAll;
                    this.newStudentDetails = changeAll;
                }
                target === 'branch' && (this.branchDetails = changeAll);
                target === 'coordinator' && (this.coordinatorDetails = changeAll);
            }
            else {
                if (param[0] === 'bank' && !this.newStudentDetails.bank) {
                    this.newStudentDetails.bank = new Array(2).fill({ bank_number: '', branch_number: '', account_number: '' });
                    this.postBank = true;
                }
                param.length > 1 ? (index ? newTarget[param[0]][index - 1][param[1]] = value : newTarget[param[0]][param[1]] = value) :
                    (index ? newTarget[param[0]][index - 1] = value : newTarget[param[0]] = value);
                target === 'student' && (param.length > 1 ?
                    (index ? this.newStudentDetails[param[0]][index - 1][param[1]] = value : this.newStudentDetails[param[0]][param[1]] = value) :
                    (index ? this.newStudentDetails[param[0]][index - 1] = value : this.newStudentDetails[param[0]] = value));
            }
        }

        if (this.allInstitution && target === 'branch') {
            const institution = this.allInstitution.find(institution => institution.identity === this.branchDetails.institution.identity &&
                institution.name === this.branchDetails.institution.name);
            const branch = institution && institution.branches.find(branch => branch.symbol === parseInt(this.branchDetails.symbol));
            if (branch) {
                this.studentDetails.fk_branch_id = branch.id;
                this.newStudentDetails.fk_branch_id = branch.id;
            }
        }
    }

    setEditStudent = (allow) => {
        this.editStudent = allow;
    }

    resetDetails = () => {
        this.studentDetails = null;
        this.studentBalanceDetails = null;
        this.branchDetails = null;
        this.coordinatorDetails = null;
        this.tableData = null;
        this.editStudent = false;
    }

    setSelectedTableTab = (tab) => {
        this.selectedTableTab = tab;
        let data = []
        switch (tab) {
            case 'payments':
                data = this.studentBalanceDetails?.payments || [];
                break;
            case 'course_enrollments':
                data = this.studentBalanceDetails?.course_enrollments || [];
                break;
            default:
                break;
        }
        this.setTableData(data);
    }

    setTableData = (data) => {
        this.tableData = data;
    }

    setCoordinatorDetails = (details) => {
        this.coordinatorDetails = details;
    }

    setBranchDetailsDetails = (details) => {
        this.branchDetails = details;
    }

    setStudentBalanceDetails = (details) => {
        const payments = details?.payments || [];
        const arrayPayments = (Object.keys(payments).map(key => ({ date: key, ...payments[key] }))).map(pay => {
            pay['course_type'] = this.studentDetails?.course_type;
            pay['coordinator_name'] = this.coordinatorDetails?.name;
            pay['institution_name'] = this.branchDetails?.institution?.name;

            return pay;
        });
        details['payments'] = arrayPayments;
        this.studentBalanceDetails = details;
        this.setTableData(details.payments);
    }

    setStudentDetails = (details) => {
        this.studentDetails = details;
    }

    fetchStudentById = (id) => {
        this.editStudent = false;
        this.tableData = null;
        Fetch.Get(`student/${id}`)
            .then(res => {
                this.setStudentDetails(res);
                this.fetchStudentBalanceById(id);
                res.fk_branch_id && this.fetchBranchById(res.fk_branch_id);
                res.fk_trend_coordinator_id && this.fetchCoordinatorById(res.fk_trend_coordinator_id);
                this.fetchInstitutionBranchCoordinator();
                this.fetchTrendCoordinator();
                this.fetchGeneralLists();
                this.fetchInstitution();
            })
            .catch(err => console.error(err))
    }

    fetchDeleteStudent = () => {
        this.studentDetails && Fetch.Delete(`student/${this.studentDetails.id}`)
            .then(res => {
                if (!res.error) {
                    sessionStorage.setItem('route', '/finance-report');
                    window.history.replaceState(null, '', '/finance-report');
                }
            })
            .catch(err => console.error(err))
    }

    fetchStudentBalanceById = (id) => {
        Fetch.Get(`finance_card/student/${id}`)
            .then(res => this.setStudentBalanceDetails(res))
            .catch(err => console.error(err))
    }

    fetchBranchById = (id) => {
        Fetch.Get(`branch/${id}`)
            .then(res => this.setBranchDetailsDetails(res))
            .catch(err => console.error(err))
    }

    fetchCoordinatorById = (id) => {
        Fetch.Get(`trend_coordinator/${id}`)
            .then(res => this.setCoordinatorDetails(res))
            .catch(err => console.error(err))
    }

    fetchInstitution = () => {
        Fetch.Get('institution')
            .then(res => this.setAllInstitution(res))
            .catch(err => console.error(err))
    }

    fetchInstitutionBranchCoordinator = () => {
        Fetch.Get('institution_branch_coordinator')
            .then(res => this.setInstitutionBranchCoordinator(res))
            .catch(err => console.error(err))
    }

    fetchTrendCoordinator = () => {
        Fetch.Get('trend_coordinator')
            .then(res => this.setTrendCoordinator(res))
            .catch(err => console.error(err))
    }

    fetchGeneralLists = () => {
        Fetch.Get('general_lists')
            .then(res => this.setGeneralLists(res))
            .catch(err => console.error(err))
    }

    fetchSaveStudentDetails = () => {
        if (this.studentDetails.bank) {
            this.studentDetails.bank[0] && this.fetchSaveBankAccount(this.studentDetails.bank[0]);
            this.studentDetails.bank[1] && this.fetchSaveBankAccount(this.studentDetails.bank[1]);
        }

        const body = { ...this.studentDetails };
        delete body['id'];
        delete body['bank']

        Fetch.Put(`student/${this.studentDetails.id}`, body)
            .then(() => this.fetchStudentById(this.studentDetails.id))
            .catch(err => console.error(err))
    }

    fetchSaveBankAccount = async (data) => {
        const id = data.id;
        const body = { ...data, attribution_id: this.studentDetails.id, attribution_type: 'student' };
        delete body['id'];

        this.postBank ? await Fetch.Post(`general_bank_account`, body)
            .catch(err => console.error(err)) :
            await Fetch.Put(`general_bank_account/${id}`, body)
                .catch(err => console.error(err))

        this.postBank = false;
    }
}

export default new StudentStore();