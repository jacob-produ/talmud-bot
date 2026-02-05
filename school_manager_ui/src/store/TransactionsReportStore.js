import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class TransactionsReportStore {
    constructor() {
        makeAutoObservable(this);
    }

    allTransactionsReport = null;
    leftTableTransactionsReport = Array(10).fill('');
    rightTableTransactionsReport = Array(10).fill('');
    leftTableTransactionsReportDownloadCSV = [];
    rightTableTransactionsReportDownloadCSV = [];
    transactionsReportFilters = [];
    transactionsReportFiltersToSend = { expense_filters: [], income_filters: [], attribution_filters: [] };
    transactionsReportFiltersDateToSend = {
        expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
        income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
        attribution_filters: []
    };
    transactionsReportFiltersDateSelectedOption = [];
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
    checkIncome = true;
    checkExpense = true;
    showPopup = false;

    setLeftTableTransactionsReportDownloadCSV = (data) => {
        const stringifyData = JSON.stringify(data);
        this.leftTableTransactionsReportDownloadCSV = JSON.parse(stringifyData).map(item =>
            Object.keys(item).reduce((obj, itemKey) => {
                item[itemKey] = item[itemKey]?.toString() || null;
                (itemKey.includes('date') || itemKey.includes('for_month')) && (item[itemKey] = item[itemKey]?.slice(0, 10).split('-').join('/') || null);
                return item;
            }, {}));
    }

    setRightTableTransactionsReportDownloadCSV = (data) => {
        const stringifyData = JSON.stringify(data);
        this.rightTableTransactionsReportDownloadCSV = JSON.parse(stringifyData).map(item =>
            Object.keys(item).reduce((obj, itemKey) => {
                item[itemKey] = item[itemKey]?.toString() || null;
                return item;
            }, {}));
    }

    setShowPopup = (show) => {
        this.showPopup = show;
    }

    changeCheckBox = (input, value) => {
        if (input === 'income') this.checkIncome = value;
        else if (input === 'expense') this.checkExpense = value;
        this.leftTableSearch = '';
        this.setLeftTableTransactionsReport(this.allTransactionsReport[0], true);
    }

    afterLeftTableUpdate = () => {
        const newRightTableTransactionsReport = this.rightTableTransactionsReport.map((rightTableItem, index) => {
            if (typeof rightTableItem === 'object' && rightTableItem !== null) {
                const countLeftTableWithSameFkId = this.leftTableTransactionsReport.filter(leftTableItem => !leftTableItem.deleted &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
                const countLeftTableWithSameFkIdToPrint = this.leftTableCheckbox.filter(leftTableCheckboxItem =>
                    leftTableCheckboxItem.item && leftTableCheckboxItem.checked &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableCheckboxItem.item[`fk_${this.selectedRightTableTab}_id`]).length;
                this.rightTableTransactionsReport[index][`all_selected`] = countLeftTableWithSameFkId === 0 ? false :
                    countLeftTableWithSameFkId === countLeftTableWithSameFkIdToPrint;
            }
            return rightTableItem;
        })
        this.rightTableTransactionsReport = newRightTableTransactionsReport;
        this.setRightTableTransactionsReportDownloadCSV(newRightTableTransactionsReport);
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
        const data = this.leftTableSearch.trim() === '' ? this.allTransactionsReport[0] : this.leftTableTransactionsReport;
        if (haveFilter) {
            let filteredData = [];
            tableSelectedItems.map(check => check.checked && (filteredData = [...filteredData, ...data.filter(rightItem =>
                rightItem[`transaction_${this.selectedRightTableTab}_id`] ? rightItem[`transaction_${this.selectedRightTableTab}_id`] === check.fk_id : true)]));
            filteredData = filteredData.filter((newSet => ({ identity }) => !newSet.has(identity) && newSet.add(identity))(new Set()));
            this.setLeftTableTransactionsReport(filteredData, true);
        }
        else
            this.setLeftTableTransactionsReport(data, true);
    }

    setRightTableCheckbox = (checked, index, item) => {
        let tableCheckbox = this.rightTableCheckbox;
        if (item) {
            // this.leftTableSearch = '';
            tableCheckbox[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableCheckbox = [...tableCheckbox];

            this.leftTableCheckbox = this.leftTableTransactionsReport.map((leftTableItem, index) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] ?
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
            const filteredSearch = (this.allTransactionsReport[tableIndex]).filter(search => search.identity?.includes(value) ||
                search.heb_attribution?.includes(value) || search.full_name?.toLowerCase()?.includes(value.toLowerCase()) ||
                search.payment_status?.includes(value) || search.amount?.toString()?.includes(value) || search.payment_method?.includes(value) ||
                (search.for_month?.slice(0, 10).split('-').reverse().join('/'))?.includes(value) ||
                (search.printing_date?.slice(0, 10).split('-').reverse().join('/'))?.includes(value) ||
                (search.transaction_date?.slice(0, 10).split('-').reverse().join('/'))?.includes(value));
            this.setLeftTableTransactionsReport(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = (this.allTransactionsReport[tableIndex])[this.selectedRightTableTab].filter(search =>
                search.name?.toLowerCase()?.includes(value.toLowerCase()) || search.balance?.toString()?.includes(value) ||
                search.balance_total?.toString()?.includes(value));
            this.setRightTableTransactionsReport(filteredSearch);
        }
    }

    setSelectedTableTab = (tableIndex, tab) => {
        if (tableIndex === 1 && this.selectedRightTableTab !== tab) {
            this.rightTableSearch = '';
            this.selectedRightTableTab = tab;
            this.setRightTableTransactionsReport((this.allTransactionsReport[tableIndex])[tab]);
            this.setRightTableSelectedItems();
        }
    }

    setTransactionsReportFiltersToSend = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex, fill) => {
        fill === 'checkAll' && (this.transactionsReportFiltersToSend = { expense_filters: [], income_filters: [], attribution_filters: [] });

        fill === 'unCheckAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => false))) :
            fill === 'checkAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => true))) :
                titleIndex - 1 > -1 && (this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex] = !this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex]);

        fill === 'unCheckAll' ?
            this.transactionsReportFilters.map(filters =>
                filters.name !== 'date_filters' && this.transactionsReportFiltersToSend[filters.name].map(filter =>
                    filter.checked = [])) :
            fill === 'checkAll' ?
                this.transactionsReportFilters.map(filters =>
                    filters.name !== 'date_filters' &&
                    filters.filters.map(filter =>
                        this.transactionsReportFiltersToSend[filters.name] = [...this.transactionsReportFiltersToSend[filters.name], { name: filter.name, checked: filter.checkboxes }])) :
                this.transactionsReportFiltersToSend[titleName].map(filter =>
                    filter.name === name && (filter.checked.some(exist => exist === checked) ?
                        (filter.checked = filter.checked.filter(value => value !== checked)) :
                        (filter.checked = [...filter.checked, checked])));
    }

    setTransactionsReportFiltersDateToSend = (date, dateIndex, fill) => {
        const selectedOption = this.transactionsReportFiltersDateSelectedOption;
        let existIndex = this.transactionsReportFiltersDateToSend[selectedOption[2]].findIndex(exist => exist.name === selectedOption[1]);

        if (existIndex === -1) {
            existIndex = this.transactionsReportFiltersDateToSend[selectedOption[2]].length;
            this.transactionsReportFiltersDateToSend[selectedOption[2]] = [...this.transactionsReportFiltersDateToSend[selectedOption[2]],
            { name: selectedOption[1], checked: ['', ''] }]
        }

        fill === 'clear' ?
            this.transactionsReportFiltersDateToSend = {
                expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
                income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }], attribution_filters: []
            } :
            (this.transactionsReportFiltersDateToSend[selectedOption[2]][existIndex]).checked[dateIndex] = `${date} 00:00`;
    }

    setTransactionsReportFiltersDateSelectedOption = (option) => {
        this.transactionsReportFiltersDateSelectedOption = option;
        const exist = this.transactionsReportFiltersDateToSend[option[2]].find(exist => exist.name === option[1]);
        exist ? this.setDateFromTo(exist.checked[0], exist.checked[1]) : this.setDateFromTo('', '');
    }

    setTransactionsReportFilters = (data) => {
        this.transactionsReportFilters = data;

        this.checkedFilters = data.map(filter => filter.name !== 'date_filters' &&
            filter.filters.map(filters => filters.checkboxes && filters.checkboxes.map(() => true))).filter(data => data && data);

        const date = data.filter(filter => filter.name === 'date_filters')[0].filters[0];
        this.transactionsReportFiltersDateSelectedOption = [date.display_name, date.name, date.filter_key];
    }

    setRightTableTransactionsReport = (data) => {
        this.rightTableCheckbox = Array(data.length).fill({ checked: false, fk_id: -1 });
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, fk_id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTableTransactionsReport = data.concat(moreRows);
        this.setRightTableTransactionsReportDownloadCSV(data);
    }

    setLeftTableTransactionsReport = (data, dontCheckRightTable) => {
        data = data.filter(row => (this.checkIncome && row.amount >= 0) || (this.checkExpense && row.amount < 0))
        this.leftTableCheckbox = Array(data.length).fill({ checked: false });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTableTransactionsReport = data.concat(moreRows);
        !dontCheckRightTable && this.setRightTableSelectedItems();
        this.setLeftTableTransactionsReportDownloadCSV(data);
    }

    setAllTransactionsReport = (data) => {
        data && data.length > 0 && (data[0] = Object.keys(data[0]).map(key => data[0][key]).flat());
        this.allTransactionsReport = data;
        data && data.length > 0 && this.setLeftTableTransactionsReport(data[0]);
        data && data.length > 1 && data[1][this.selectedRightTableTab] && this.setRightTableTransactionsReport(data[1][this.selectedRightTableTab])
    }

    fetchFilteredTransactionsReport = (body) => {
        this.setAllTransactionsReport(null);
        Fetch.Post('transactions_report', body)
            .then(res => this.setAllTransactionsReport(res))
            .catch(err => console.error(err))
    }

    fetchTransactionsReportFilters = async () => {
        return await !sessionStorage.getItem('reload') && Fetch.Get('transactions_report/filters')
            .then(res => this.setTransactionsReportFilters(res))
            .catch(err => console.error(err))
    }

    resetCheckbox = () => {
        this.leftTableCheckbox = Array(this.leftTableTransactionsReport.length).fill({ checked: false });
    }

    fetchRestoreExpense = () => {
        const body = { expense_ids: this.leftTableCheckbox.filter(data => data.checked).map(data => data.item.id) };

        return body.expense_ids.length > 0 ? Fetch.Put('transactions_report', body)
            .then((res) => {
                const withError = res.filter(data => data.error);
                const withoutError = res.filter(data => !data.error);
                const messageWithError = withError.length > 0 ? `(${withError.length}) ${withError[0].message}` : '';
                const messageWithoutError = withoutError.length > 0 ? `(${withoutError.length}) ${withoutError[0].message}` : '';
                this.changeExpenseMessage(`${messageWithError} ${messageWithoutError}`);
                this.resetCheckbox();
            })
            .catch(err => console.error(err)) :
            this.changeExpenseMessage('No data');
    }

    fetchRawTable = async () => {
        const body = {
            tables: ["expense", "income"],
            start_date: this.dateFrom.split('-').reverse().join('/'),
            end_date: this.dateTo.split('-').reverse().join('/'),
            dates_attributes: ["created_date", "created_date"]
        }

        return await Fetch.Post('raw_table', body, true)
            .catch(err => console.error(err))
    }

    fetchGoogleSheets = async (data) => {
        return await Fetch.Post('transactions_report/export', data, true)
            .catch(err => console.error(err))
    }
}

export default new TransactionsReportStore();