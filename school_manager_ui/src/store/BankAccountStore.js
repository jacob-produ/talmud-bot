import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class BankAccountStore {
    constructor() {
        makeAutoObservable(this);
    }

    allBankAccount = null;
    allCurrentAccount = null;
    leftTableBankAccount = Array(10).fill('');
    rightTableBankAccount = Array(10).fill('');
    dateFrom = '';
    dateTo = '';
    leftTableHeight = 0;
    rightTableHeight = 0;
    leftTableSearch = '';
    rightTableSearch = '';
    rightTableSelectedItems = [];
    selectedRightTableTab = 'bank_account';
    checkBoxFilter = { linked: true, unlinked: true };

    changeCheckBoxFilter = (check, position) => {
        this.checkBoxFilter[position] = check;
        this.setLeftTableBankAccount(this.allBankAccount);
    }

    setRightTableSelectedItems = (checked, index, item) => {
        let tableSelectedItems = this.rightTableSelectedItems;
        if (item) {
            this.leftTableSearch = '';
            tableSelectedItems[index] = { checked: !tableSelectedItems[index].checked, id: item['id'] };
            this.rightTableSelectedItems = [...tableSelectedItems];
        }
        const haveFilter = tableSelectedItems.some(exist => exist.checked);
        const data = this.leftTableSearch.trim() === '' ? this.allCurrentAccount : this.leftTableBankAccount;
        if (haveFilter) {
            let filteredData = [];
            tableSelectedItems.map(check => check.checked && (filteredData = [...filteredData, ...data.filter(rightItem =>
                rightItem[`fk_${this.selectedRightTableTab}_id`] ? rightItem[`fk_${this.selectedRightTableTab}_id`] === check.id : true)]));
            filteredData = filteredData.filter((newSet => ({ id }) => !newSet.has(id) && newSet.add(id))(new Set()));
            this.setLeftTableBankAccount(filteredData, true);
        }
        else
            this.setLeftTableBankAccount(data, true);
    }

    setLeftTableHeight = (height) => {
        this.leftTableHeight = height;
    }

    setRightTableHeight = (height) => {
        this.rightTableHeight = height;
    }

    setDateFromTo = (from, to) => {
        from ? (this.dateFrom = from) : from === '' && (this.dateFrom = '');
        to ? (this.dateTo = to) : to === '' && (this.dateTo = '');
        this.dateFrom && this.dateTo && this.dateFrom > this.dateTo && (this.dateTo = '');
    }

    setTableSearch = (tableIndex, value) => {
        if (tableIndex === 0) {
            this.leftTableSearch = value;
            const filteredSearch = this.allCurrentAccount.filter(search => search.date.includes(value) ||
                search.value_date.includes(value) || search.transaction_amount.toString().includes(value) ||
                search.balance.toString().includes(value) || search.reference_number.includes(value));
            this.setLeftTableBankAccount(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = this.allBankAccount.filter(search =>
                search.account_number.toString().includes(value) || search.balance.toString().includes(value) ||
                search.cash.toString().includes(value) || search.commitment.toString().includes(value) ||
                search.flow.toString().includes(value) || search.institution_name.toLowerCase().includes(value.toLowerCase()) ||
                search.line_of_credit.toString().includes(value) || search.loan.toString().includes(value));
            this.setRightTableBankAccount(filteredSearch);
        }
    }

    setLeftTableBankAccount = (data, dontCheckRightTable) => {
        data = this.checkBoxFilter.linked && this.checkBoxFilter.unlinked ? data :
            this.checkBoxFilter.linked ? data.filter(bankDetail => bankDetail.is_linked) :
                this.checkBoxFilter.unlinked ? data.filter(bankDetail => !bankDetail.is_linked) : [];
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTableBankAccount = data.concat(moreRows);

        !dontCheckRightTable && this.setRightTableSelectedItems();
    }

    setRightTableBankAccount = (data) => {
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTableBankAccount = data.concat(moreRows);
    }

    setAllCurrentAccount = (currentAccount) => {
        this.allCurrentAccount = currentAccount.data ? currentAccount.data : currentAccount;
        this.setLeftTableBankAccount(currentAccount.data ? currentAccount.data : currentAccount);
    }

    setAllBankAccount = (bankAccount) => {
        this.allBankAccount = bankAccount.data ? bankAccount.data : bankAccount;
        this.setRightTableBankAccount(bankAccount.data ? bankAccount.data : bankAccount);
    }

    fetchBankAccount = () => {
        Fetch.Get(`bank_account?verbose=${encodeURIComponent(true)}`)
            .then(res => this.setAllBankAccount(res))
            .catch(err => console.error(err))
    }

    fetchCurrentAccount = () => {
        this.allCurrentAccount = null;

        const encodeDate = (date) => encodeURIComponent(date.slice(0, 10).split('-').reverse().join('/'));
        const start_date = this.dateFrom === '' ? null : encodeDate(this.dateFrom);
        const end_date = this.dateTo === '' ? null : encodeDate(this.dateTo);

        // const start_date = '01/07/2020';
        // const end_date = '01/07/2021';

        Fetch.Get(`current_account${start_date && end_date ? `?start_date=${start_date}&end_date=${end_date}` : ''}`)
            .then(res => this.setAllCurrentAccount(res))
            .catch(err => console.error(err))
    }

    // #region Make Link Popup
    index = 0;
    rightBankAccount = null;
    donator = null;
    trendCoordinator = null;
    student = null;
    supplier = null;
    msv = null;
    comment = null;
    makeLink = null;
    allDonators = null;
    allTrendCoordinator = null;
    allStudents = null;
    allSuppliers = null;
    allMSV = null;
    ownDonator = null;
    ownTrendCoordinator = null;
    ownStudent = null;
    ownSupplier = null;
    ownMsv = null;
    loader = false;
    existDonator = null;
    existTrendCoordinator = null;
    existStudent = null;
    existSupplier = null;
    existMsv = null;

    setLoader = (value) => {
        this.loader = value;
    }

    setOwnDonator = (value) => {
        this.ownDonator = value;
    }

    setOwnTrendCoordinator = (value) => {
        this.ownTrendCoordinator = value;
    }

    setOwnStudent = (value) => {
        this.ownStudent = value;
    }

    setOwnSupplier = (value) => {
        this.ownSupplier = value;
    }

    setOwnMsv = (value) => {
        this.ownMsv = value;
    }

    setAllMSV = (allMSV) => {
        this.allMSV = allMSV;
        allMSV?.length === 0 && this.setMSV('אין רשומות');
    }

    setAllDonators = (allDonators) => {
        this.allDonators = allDonators;
        allDonators?.length === 0 && this.setDonator('אין רשומות');
    }

    setAllTrendCoordinator = (allTrendCoordinator) => {
        this.allTrendCoordinator = allTrendCoordinator;
        allTrendCoordinator?.length === 0 && this.setTrendCoordinator('אין רשומות');
    }

    setAllStudents = (allStudents) => {
        this.allStudents = allStudents;
        allStudents?.length === 0 && this.setStudent('אין רשומות');
    }

    setAllSuppliers = (allSuppliers) => {
        this.allSuppliers = allSuppliers;
        allSuppliers?.length === 0 && this.setSupplier('אין רשומות');
    }

    setMakeLink = (item) => {
        this.makeLink = item;
        item && this.fetchMSV(item.transaction_amount, item.date.slice(0, 10))
            .then(res => {
                this.setComment(item.comment);

                const data = item.expense?.length > 0 ? item.expense[0] : item.income?.length > 0 ? item.income[0] : null;
                if (data) {
                    const donator = data.fk_donator_id !== null && this.allDonators.find(d => d.id === data.fk_donator_id);
                    const trend = data.fk_trend_coordinator_id !== null && this.allTrendCoordinator.find(t => t.id === data.fk_trend_coordinator_id);
                    const student = data.attribution === 'student' && data.attribution_id !== null && this.allStudents.find(s => s.id === data.attribution_id);
                    const supplier = data.attribution === 'supplier' && data.attribution_id !== null && this.allSuppliers.find(s => s.id === data.attribution_id);
                    const msv = !(item.income?.length !== 0) && data.fk_msv_file_id !== null && res?.find(m => m.id === data.fk_msv_file_id);

                    if (donator) {
                        const value = `${donator.first_name} ${donator.last_name} - ${donator.identity}`;
                        this.setDonator(value);
                        this.setOwnDonator(donator);
                    }

                    if (trend) {
                        const value = `${trend.name} - ${trend.id}`;
                        this.setTrendCoordinator(value);
                        this.setOwnTrendCoordinator(value);
                    }

                    if (student) {
                        const value = `${student.first_name} ${student.last_name} - ${student.identity}`;
                        this.setStudent(value);
                        this.setOwnStudent(value);
                    }

                    if (supplier) {
                        const value = `${supplier.name} - ${supplier.identity}`;
                        this.setSupplier(value);
                        this.setOwnSupplier(value);
                    }

                    if (msv) {
                        const value = `${msv.amount} - ${msv.date} - ${msv.id}`;
                        this.setMSV(value);
                        this.setOwnMsv(value);
                    }
                }
            });
    }

    setIndex = (value) => {
        this.index = value;
    }

    setRightBankAccount = (value) => {
        this.rightBankAccount = value;
    }

    setDonator = (value) => {
        this.donator = value && value.trim() !== '' ? value : null;

        const donator = value && value.split(' - ');
        this.existDonator = value ? this.allDonators?.find(d => d.identity === donator[donator.length - 1])?.id : null;
    }

    setTrendCoordinator = (value) => {
        this.trendCoordinator = value && value.trim() !== '' ? value : null;

        const trendCoordinator = value && value.split(' - ');
        this.existTrendCoordinator = value ? this.allTrendCoordinator?.find(t => `${t.id}` === trendCoordinator[trendCoordinator.length - 1])?.id : null;
    }

    setStudent = (value) => {
        this.student = value && value.trim() !== '' ? value : null;

        const student = value && value.split(' - ');
        this.existStudent = value ? this.allStudents?.find(s => s.identity === student[student.length - 1])?.id : null;
    }

    setSupplier = (value) => {
        this.supplier = value && value.trim() !== '' ? value : null;

        const supplier = value && value.split(' - ');
        this.existSupplier = value ? this.allSuppliers?.find(s => s.identity === supplier[supplier.length - 1])?.id : null;
    }

    setMSV = (value) => {
        this.msv = value && value.trim() !== '' ? value : null;

        const msv = value && value.split(' - ');
        this.existMsv = value ? this.allMSV?.find(m => `${m.id}` === msv[msv.length - 1])?.id : null;
    }

    setComment = (value) => {
        this.comment = value && value.trim() !== '' ? value : null;
    }

    fetchTrendCoordinator = () => {
        Fetch.Get('link_ca/trend_coordinator')
            .then(res => this.setAllTrendCoordinator(res))
            .catch(err => console.error(err))
    }

    fetchStudens = () => {
        Fetch.Get('link_ca/student')
            .then(res => this.setAllStudents(res))
            .catch(err => console.error(err))
    }

    fetchSuppliers = () => {
        Fetch.Get('link_ca/supplier')
            .then(res => this.setAllSuppliers(res))
            .catch(err => console.error(err))
    }

    fetchMSV = async (amount, date) => {
        return await Fetch.Get(`link_ca/msv?amount=${amount}&date=${date}`)
            .then(res => this.setAllMSV(res.error ? [] : res))
            .catch(err => console.error(err))
    }

    fetchDonators = () => {
        Fetch.Get('donator')
            .then(res => this.setAllDonators(res))
            .catch(err => console.error(err))
    }

    fetchSave = () => {
        this.setLoader(true);

        if (this.donator !== this.ownTrendCoordinator) {
            const body = {
                fk_current_account_id: this.makeLink.id,
                ca_amount: this.makeLink.transaction_amount,
                fk_trend_coordinator_id: this.existDonator,
            }

            var trendCoordinatorFetch = Fetch.Put('link_ca/donator', body)
                .catch(err => console.error(err));
        }


        if (this.trendCoordinator !== this.ownTrendCoordinator) {
            const body = {
                fk_current_account_id: this.makeLink.id,
                ca_amount: this.makeLink.transaction_amount,
                fk_trend_coordinator_id: this.existTrendCoordinator,
            }

            var trendCoordinatorFetch = Fetch.Put('link_ca/trend_coordinator', body)
                .catch(err => console.error(err));
        }

        if (this.student !== this.ownStudent) {
            const body = {
                fk_current_account_id: this.makeLink.id,
                ca_amount: this.makeLink.transaction_amount,
                attribution: 'student',
                attribution_id: this.existStudent,
            }

            var studentFetch = Fetch.Put('link_ca/student', body)
                .catch(err => console.error(err));
        }

        if (this.supplier !== this.ownSupplier) {
            const body = {
                fk_current_account_id: this.makeLink.id,
                ca_amount: this.makeLink.transaction_amount,
                attribution: 'supplier',
                attribution_id: this.existSupplier,
            }

            var supplierFetch = Fetch.Put('link_ca/supplier', body)
                .catch(err => console.error(err));
        }


        if (this.msv !== this.ownMsv) {
            const msv = this.ownMsv && this.ownMsv.split(' - ');
            const msvID = this.existMsv || msv ? msv[msv.length - 1] : null;

            if (msvID !== null) {
                const body = {
                    fk_current_account_id: this.makeLink.id,
                    fk_msv_file_id: msvID,
                    delete: this.existMsv !== null ? false : true
                }

                var msvFetch = Fetch.Put('link_ca/msv', body)
                    .catch(err => console.error(err));
            }
        }


        if (this.comment !== this.makeLink.comment) {
            const body = { comment: this.comment };
            var commentFetch = Fetch.Put(`current_account/${this.makeLink.id}`, body)
                .catch(err => console.error(err));
        }

        const ClearDataIfNotExist = () => {
            !this.existTrendCoordinator && this.setTrendCoordinator(null);
            !this.existSupplier && this.setSupplier(null);
            !this.existStudent && this.setStudent(null);
            !this.existMsv && this.setMSV(null);
        }

        Promise.all([trendCoordinatorFetch, studentFetch, supplierFetch, msvFetch, commentFetch])
            .then(() => {
                this.setLoader(false);
                this.fetchCurrentAccount();
                ClearDataIfNotExist();
            })
            .catch(err => console.error(err))
    }
    // #endregion
}

export default new BankAccountStore();