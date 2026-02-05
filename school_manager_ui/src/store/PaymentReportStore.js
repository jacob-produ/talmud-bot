import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class PaymentReportStore {
    constructor() {
        makeAutoObservable(this);
    }

    allFinanceReport = null;
    leftTableFinanceReport = Array(10).fill('');
    rightTableFinanceReport = Array(10).fill('');
    leftTableFinanceReportDownloadCSV = [];
    rightTableFinanceReportDownloadCSV = [];
    financeReportFilters = [];
    financeReportFiltersToSend = { expense_filters: [], income_filters: [], student_filters: [] };
    financeReportFiltersDateToSend = {
        expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
        income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
        student_filters: []
    };
    financeReportFiltersDateSelectedOption = [];
    selectedLeftTableTab = 'student';
    selectedRightTableTab = 'institution';
    leftTableSearch = '';
    rightTableSearch = '';
    dateFrom = ''; // `${new Date().getFullYear()}-01-01`;
    dateTo = ''; // `${new Date().toISOString().slice(0, 10)}`;
    leftTableHeight = 0;
    rightTableHeight = 0;
    leftTableCheckbox = [];
    rightTableCheckbox = [];
    rightTableSelectedItems = [];
    checkedFilters = [];
    expenseMessage = '';

    setLeftTableFinanceReportDownloadCSV = (data) => {
        const stringifyData = JSON.stringify(data);
        this.leftTableFinanceReportDownloadCSV = JSON.parse(stringifyData).map(item =>
            Object.keys(item).reduce((obj, itemKey) => {
                item[itemKey] = item[itemKey]?.toString() || null;
                return item;
            }, {}));
    }

    setRightTableFinanceReportDownloadCSV = (data) => {
        const stringifyData = JSON.stringify(data);
        this.rightTableFinanceReportDownloadCSV = JSON.parse(stringifyData).map(item =>
            Object.keys(item).reduce((obj, itemKey) => {
                item[itemKey] = item[itemKey]?.toString() || null;
                console.log(item);
                return item;
            }, {}));
    }

    afterLeftTableUpdate = () => {
        const newRightTableFinanceReport = this.rightTableFinanceReport.map((rightTableItem, index) => {
            if (typeof rightTableItem === 'object' && rightTableItem !== null) {
                const countLeftTableWithSameFkId = this.leftTableFinanceReport.filter(leftTableItem => !leftTableItem.deleted &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
                const countLeftTableWithSameFkIdToPrint = this.leftTableCheckbox.filter(leftTableCheckboxItem =>
                    leftTableCheckboxItem && leftTableCheckboxItem.item && leftTableCheckboxItem.checked &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableCheckboxItem.item[`fk_${this.selectedRightTableTab}_id`]).length;
                this.rightTableFinanceReport[index][`all_selected`] = countLeftTableWithSameFkId === 0 ? false :
                    countLeftTableWithSameFkId === countLeftTableWithSameFkIdToPrint;
            }
            return rightTableItem;
        })
        this.rightTableFinanceReport = newRightTableFinanceReport
        this.setRightTableFinanceReportDownloadCSV(newRightTableFinanceReport);
    }

    changeExpenseMessage = (msg) => {
        this.expenseMessage = msg;
    }

    setCheckedFilters = (checkbox) => {
        this.checkedFilters = checkbox;
    }

    setRightTableSelectedItems = (checked, index, item) => {
        let tableSelectedItems = this.rightTableSelectedItems;
        if (item) {
            this.leftTableSearch = '';
            tableSelectedItems[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableSelectedItems = [...tableSelectedItems];
        }

        const haveFilter = tableSelectedItems.some(exist => exist.checked);
        const data = this.leftTableSearch.trim() === '' ? this.allFinanceReport[0][this.selectedLeftTableTab] : this.leftTableFinanceReport;
        if (haveFilter) {
            let filteredData = [];
            tableSelectedItems.map(check => check.checked && (filteredData = [...filteredData, ...data.filter(rightItem =>
                rightItem[`fk_${this.selectedRightTableTab}_id`] ? rightItem[`fk_${this.selectedRightTableTab}_id`] === check.fk_id : true)]));
            filteredData = filteredData.filter((newSet => ({ identity }) => !newSet.has(identity) && newSet.add(identity))(new Set()));
            this.setLeftTableFinanceReport(filteredData, true);
        }
        else
            this.setLeftTableFinanceReport(data, true);
    }

    setRightTableCheckbox = (checked, index, item) => {
        let tableCheckbox = this.rightTableCheckbox;
        if (item) {
            // this.leftTableSearch = '';
            tableCheckbox[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableCheckbox = [...tableCheckbox];

            this.leftTableCheckbox = this.leftTableFinanceReport.map((leftTableItem, index) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] && !leftTableItem.deleted ?
                    ({ checked, item: leftTableItem }) : this.leftTableCheckbox[index])
        }
    }

    setLeftTableCheckbox = (checked, index, item) => {
        let tableCheckbox = this.leftTableCheckbox;
        tableCheckbox[index] = {
            checked, item
        };

        this.leftTableCheckbox = [...tableCheckbox];
    }

    setLeftTableHeight = (height) => {
        this.leftTableHeight = height;
    }

    setRightTableHeight = (height) => {
        this.rightTableHeight = height;
    }

    setDateFromTo = (from, to) => {
        from ? (this.dateFrom = from.slice(0, 10).split('/').reverse().join('-')) : from === '' && (this.dateFrom = '');
        to ? (this.dateTo = to.slice(0, 10).split('/').reverse().join('-')) : to === '' && (this.dateTo = '');
    }

    setTableSearch = (tableIndex, value) => {
        if (tableIndex === 0) {
            this.leftTableSearch = value;
            const filteredSearch = (this.allFinanceReport[tableIndex])[this.selectedLeftTableTab].filter(search => search.identity.includes(value) ||
                search.full_name.toLowerCase().includes(value.toLowerCase()) || search.income_sum.toString().includes(value) ||
                search.expense_sum.toString().includes(value) || search.balance.toString().includes(value) ||
                search.balance_total.toString().includes(value));
            this.setLeftTableFinanceReport(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = (this.allFinanceReport[tableIndex])[this.selectedRightTableTab].filter(search =>
                search.name.toLowerCase().includes(value.toLowerCase()) || search.income_sum.toString().includes(value) ||
                search.expense_sum.toString().includes(value) || search.balance.toString().includes(value) ||
                search.balance_total.toString().includes(value));
            this.setRightTableFinanceReport(filteredSearch);
        }
    }

    setSelectedTableTab = (tableIndex, tab) => {
        if (tableIndex === 0 && this.selectedLeftTableTab !== tab) {
            this.leftTableSearch = '';
            this.selectedLeftTableTab = tab;
            this.setLeftTableFinanceReport((this.allFinanceReport[tableIndex])[tab]);
        }
        else if (tableIndex === 1 && this.selectedRightTableTab !== tab) {
            this.rightTableSearch = '';
            this.selectedRightTableTab = tab;
            this.setRightTableFinanceReport((this.allFinanceReport[tableIndex])[tab]);
            this.setRightTableSelectedItems();
        }
    }

    setFinanceReportFiltersToSend = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex, fill) => {
        fill === 'checkAll' && (this.financeReportFiltersToSend = { expense_filters: [], income_filters: [], student_filters: [] });

        fill === 'unCheckAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => false))) :
            fill === 'checkAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => true))) :
                titleIndex - 1 > -1 && (this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex] = !this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex]);

        fill === 'unCheckAll' ?
            this.financeReportFilters.map(filters =>
                filters.name !== 'date_filters' && this.financeReportFiltersToSend[filters.name].map(filter =>
                    filter.checked = [])) :
            fill === 'checkAll' ?
                this.financeReportFilters.map(filters =>
                    filters.name !== 'date_filters' &&
                    filters.filters.map(filter =>
                        this.financeReportFiltersToSend[filters.name] = [...this.financeReportFiltersToSend[filters.name], { name: filter.name, checked: filter.checkboxes }])) :
                this.financeReportFiltersToSend[titleName].map(filter =>
                    filter.name === name && (filter.checked.some(exist => exist === checked) ?
                        (filter.checked = filter.checked.filter(value => value !== checked)) :
                        (filter.checked = [...filter.checked, checked])));
    }

    setFinanceReportFiltersDateToSend = (date, dateIndex, fill) => {
        const selectedOption = this.financeReportFiltersDateSelectedOption;
        let existIndex = this.financeReportFiltersDateToSend[selectedOption[2]]?.findIndex(exist => exist.name === selectedOption[1]);

        if (existIndex === -1) {
            existIndex = this.financeReportFiltersDateToSend[selectedOption[2]].length;
            this.financeReportFiltersDateToSend[selectedOption[2]] = [...this.financeReportFiltersDateToSend[selectedOption[2]],
            { name: selectedOption[1], checked: ['', ''] }]
        }

        fill === 'clear' || selectedOption.length === 0 ?
            this.financeReportFiltersDateToSend = {
                expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
                income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }], student_filters: []
            } :
            (this.financeReportFiltersDateToSend[selectedOption[2]][existIndex]).checked[dateIndex] = `${date} 00:00`;
    }

    setFinanceReportFiltersDateSelectedOption = (option) => {
        this.financeReportFiltersDateSelectedOption = option;
        const exist = this.financeReportFiltersDateToSend[option[2]].find(exist => exist.name === option[1]);
        exist ? this.setDateFromTo(exist.checked[0], exist.checked[1]) : this.setDateFromTo('', '');
    }

    setFinanceReportFilters = (data) => {
        this.financeReportFilters = data;

        this.checkedFilters = data.map(filter => filter.name !== 'date_filters' &&
            filter.filters.map(filters => filters.checkboxes && filters.checkboxes.map(() => true))).filter(data => data && data);

        const date = data.filter(filter => filter.name === 'date_filters')[0].filters[0];
        this.financeReportFiltersDateSelectedOption = [date.display_name, date.name, date.filter_key];
    }

    setRightTableFinanceReport = (data) => {
        this.rightTableCheckbox = Array(data.length).fill({ checked: false, fk_id: -1 });
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, fk_id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTableFinanceReport = data.concat(moreRows);
        this.setRightTableFinanceReportDownloadCSV(data);
    }

    setLeftTableFinanceReport = (data, dontCheckRightTable) => {
        this.leftTableCheckbox = Array(data.length).fill({ checked: false });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTableFinanceReport = data.concat(moreRows);
        !dontCheckRightTable && this.setRightTableSelectedItems();
        this.setLeftTableFinanceReportDownloadCSV(this.leftTableFinanceReport);
    }

    setAllFinanceReport = (data) => {
        this.allFinanceReport = data;
        data && data.length > 0 && data[0][this.selectedLeftTableTab] && this.setLeftTableFinanceReport(data[0][this.selectedLeftTableTab]);
        data && data.length > 1 && data[1][this.selectedRightTableTab] && this.setRightTableFinanceReport(data[1][this.selectedRightTableTab])
    }

    fetchFilteredFinanceReport = (body) => {
        this.setAllFinanceReport(null);
        Fetch.Post('finance_report', body)
            .then(res => this.setAllFinanceReport(res))
            .catch(err => console.error(err))
    }

    fetchFinanceReportFilters = async () => {
        return await !sessionStorage.getItem('reload') && Fetch.Get('finance_report/filters')
            .then(res => this.setFinanceReportFilters(res))
            .catch(err => console.error(err))
    }

    resetCheckbox = () => {
        this.leftTableCheckbox = Array(this.leftTableFinanceReport.length).fill({ checked: false });
    }

    fetchExpense = () => {
        const body = this.leftTableCheckbox.filter(data => data.checked)
            .map(data => ({
                attribution: data.item.attribution, attribution_id: data.item.attribution_id, fk_branch_id: data.item.fk_branch_id,
                fk_institution_id: data.item.fk_institution_id, fk_trend_coordinator_id: data.item.fk_trend_coordinator_id,
                payment_method: data.item.payment_method, amount: data.item.expense_sum,
                fk_bank_account_id: data.item.fk_bank_account_id, payment_status: 'טיוטה'
            }));

        body.length > 0 && Fetch.Post('finance_report?pay=true', body)
            .then((res) => { this.changeExpenseMessage(res.message.value); this.resetCheckbox(); })
            .catch(err => console.error(err))
    }
    fetchGoogleSheets = async (data) => {
        console.log(data);
        return await Fetch.Post('finance_report/export', data, false)
            .catch(err => console.error(err))
    }
}

export default new PaymentReportStore();