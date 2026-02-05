import { makeAutoObservable } from 'mobx';
import * as Fetch from '../../Fetch';

class FinanceReportStore {
    constructor() {
        makeAutoObservable(this);
    }
    allFinanceReport: any = null;
    leftTableFinanceReport: any = Array(10).fill('');
    rightTableFinanceReport: any = Array(10).fill('');
    leftTableFinanceReportDownloadCSV: any = [];
    rightTableFinanceReportDownloadCSV: any = [];
    financeReportFilters: any = [];
    financeReportFiltersToSend: any = { expense_filters: [], income_filters: [], student_filters: [] };
    financeReportFiltersDateToSend: any = {
        expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
        income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
        student_filters: []
    };
    financeReportFiltersDateSelectedOption: any = [];
    selectedLeftTableTab: string = 'student';
    selectedRightTableTab: string = 'institution';
    leftTableSearch: string = '';
    rightTableSearch: string = '';
    dateFrom: string = ''; // `${new Date().getFullYear()}-01-01`;
    dateTo: string = ''; // `${new Date().toISOString().slice(0, 10)}`;
    leftTableHeight: number = 0;
    rightTableHeight: number = 0;
    leftTableCheckbox: any = [];
    rightTableCheckbox: any = [];
    rightTableSelectedItems: any = [];
    checkedFilters: any = [];
    expenseMessage: string = '';

    leftTableCSV_data = [
        { label: 'מזהה', key: 'identity' },
        { label: 'שם מלא', key: 'full_name' },
        { label: 'הכנסות', key: 'income_sum' },
        { label: 'הוצאות', key: 'expense_sum' },
        { label: 'יתרה', key: 'balance' },
        { label: 'יתרה כוללת', key: 'balance_total' }
    ];

    rightTableCSV_data = [
        { label: 'שם', key: 'name' },
        { label: 'הכנסות', key: 'income_sum' },
        { label: 'הוצאות', key: 'expense_sum' },
        { label: 'יתרה', key: 'balance' },
        { label: 'יתרה כוללת', key: 'balance_total' }
    ];

    setLeftTableFinanceReportDownloadCSV = (data: any) => {
        const stringifyData = JSON.stringify(data);
        this.leftTableFinanceReportDownloadCSV = JSON.parse(stringifyData).map((item: any) =>
            Object.keys(item).reduce((obj, itemKey) => {
                item[itemKey] = item[itemKey]?.toString() || null;
                return item;
            }, {}));
    }

    setRightTableFinanceReportDownloadCSV = (data: any) => {
        const stringifyData = JSON.stringify(data);
        this.rightTableFinanceReportDownloadCSV = JSON.parse(stringifyData).map((item: any) =>
            Object.keys(item).reduce((obj, itemKey) => {
                item[itemKey] = item[itemKey]?.toString() || null;
                return item;
            }, {}));
    }

    afterLeftTableUpdate = () => {
        const newRightTableFinanceReport = this.rightTableFinanceReport.map((rightTableItem: any, index: number) => {
            if (typeof rightTableItem === 'object' && rightTableItem !== null) {
                const countLeftTableWithSameFkId = this.leftTableFinanceReport.filter((leftTableItem: any) => !leftTableItem.deleted &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
                const countLeftTableWithSameFkIdToPrint = this.leftTableCheckbox.filter((leftTableCheckboxItem: any) =>
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

    changeExpenseMessage = (msg: string) => {
        this.expenseMessage = msg;
    }

    setCheckedFilters = (checkbox: any) => {
        this.checkedFilters = checkbox;
    }

    setRightTableSelectedItems = (checked?: boolean, index?: number, item?: any) => {
        let tableSelectedItems = this.rightTableSelectedItems;
        if (item && index) {
            this.leftTableSearch = '';
            tableSelectedItems[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableSelectedItems = [...tableSelectedItems];
        }

        const haveFilter = tableSelectedItems.some((exist: any) => exist.checked);
        const data = this.leftTableSearch.trim() === '' ? this.allFinanceReport[0][this.selectedLeftTableTab] : this.leftTableFinanceReport;
        if (haveFilter) {
            let filteredData: any = [];
            tableSelectedItems.map((check: any) => check.checked && (filteredData = [...filteredData, ...data.filter((rightItem: any) =>
                rightItem[`fk_${this.selectedRightTableTab}_id`] ? rightItem[`fk_${this.selectedRightTableTab}_id`] === check.fk_id : true)]));
            filteredData = filteredData.filter(((newSet: any) => (data: any) => !newSet.has(data.identity) && newSet.add(data.identity))(new Set()));
            this.setLeftTableFinanceReport(filteredData, true);
        }
        else
            this.setLeftTableFinanceReport(data, true);
    }

    setRightTableCheckbox = (checked: boolean, index: number, item: any) => {
        let tableCheckbox = this.rightTableCheckbox;
        if (item) {
            // this.leftTableSearch = '';
            tableCheckbox[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableCheckbox = [...tableCheckbox];

            this.leftTableCheckbox = this.leftTableFinanceReport.map((leftTableItem: any, index: number) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] && !leftTableItem.deleted ?
                    ({ checked, item: leftTableItem }) : this.leftTableCheckbox[index])
        }
    }

    setLeftTableCheckbox = (checked: boolean, index: number, item: any) => {
        let tableCheckbox = this.leftTableCheckbox;
        tableCheckbox[index] = {
            checked, item
        };

        this.leftTableCheckbox = [...tableCheckbox];
    }

    setLeftTableHeight = (height: number) => {
        this.leftTableHeight = height;
    }

    setRightTableHeight = (height: number) => {
        this.rightTableHeight = height;
    }

    setDateFromTo = (from: string | null, to?: string) => {
        from ? (this.dateFrom = from.slice(0, 10).split('/').reverse().join('-')) : from === '' && (this.dateFrom = '');
        to ? (this.dateTo = to.slice(0, 10).split('/').reverse().join('-')) : to === '' && (this.dateTo = '');
    }

    setTableSearch = (tableIndex: number, value: string) => {
        if (tableIndex === 0) {
            this.leftTableSearch = value;
            const filteredSearch = (this.allFinanceReport[tableIndex])[this.selectedLeftTableTab].filter((search: any) => search.identity.includes(value) ||
                search.full_name.toLowerCase().includes(value.toLowerCase()) || search.income_sum.toString().includes(value) ||
                search.expense_sum.toString().includes(value) || search.balance.toString().includes(value) ||
                search.balance_total.toString().includes(value));
            this.setLeftTableFinanceReport(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = (this.allFinanceReport[tableIndex])[this.selectedRightTableTab].filter((search: any) =>
                search.name.toLowerCase().includes(value.toLowerCase()) || search.income_sum.toString().includes(value) ||
                search.expense_sum.toString().includes(value) || search.balance.toString().includes(value) ||
                search.balance_total.toString().includes(value));
            this.setRightTableFinanceReport(filteredSearch);
        }
    }

    setSelectedTableTab = (tableIndex: number, tab: string) => {
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

    setFinanceReportFiltersToSend = (titleName: any, name: any, checked: any, titleIndex: any, filterIndex: any, checkboxIndex: any, fill?: any) => {
        fill === 'checkAll' && (this.financeReportFiltersToSend = { expense_filters: [], income_filters: [], student_filters: [] });

        fill === 'unCheckAll' ? this.checkedFilters = this.checkedFilters.map((checkboxes: any) => checkboxes.map((checkbox: any) => checkbox.map(() => false))) :
            fill === 'checkAll' ? this.checkedFilters = this.checkedFilters.map((checkboxes: any) => checkboxes.map((checkbox: any) => checkbox.map(() => true))) :
                titleIndex - 1 > -1 && (this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex] = !this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex]);

        fill === 'unCheckAll' ?
            this.financeReportFilters.map((filters: any) =>
                filters.name !== 'date_filters' && this.financeReportFiltersToSend[filters.name].map((filter: any) =>
                    filter.checked = [])) :
            fill === 'checkAll' ?
                this.financeReportFilters.map((filters: any) =>
                    filters.name !== 'date_filters' &&
                    filters.filters.map((filter: any) =>
                        this.financeReportFiltersToSend[filters.name] = [...this.financeReportFiltersToSend[filters.name], { name: filter.name, checked: filter.checkboxes }])) :
                this.financeReportFiltersToSend[titleName].map((filter: any) =>
                    filter.name === name && (filter.checked.some((exist: string) => exist === checked) ?
                        (filter.checked = filter.checked.filter((value: string) => value !== checked)) :
                        (filter.checked = [...filter.checked, checked])));
    }

    setFinanceReportFiltersDateToSend = (date?: any, dateIndex?: number | null, fill?: string) => {
        const selectedOption = this.financeReportFiltersDateSelectedOption;
        let existIndex = this.financeReportFiltersDateToSend[selectedOption[2]].findIndex((exist: any) => exist.name === selectedOption[1]);

        if (existIndex === -1) {
            existIndex = this.financeReportFiltersDateToSend[selectedOption[2]].length;
            this.financeReportFiltersDateToSend[selectedOption[2]] = [...this.financeReportFiltersDateToSend[selectedOption[2]],
            { name: selectedOption[1], checked: ['', ''] }]
        }

        fill === 'clear' ?
            this.financeReportFiltersDateToSend = {
                expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
                income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }], student_filters: []
            } :
            date && dateIndex && ((this.financeReportFiltersDateToSend[selectedOption[2]][existIndex]).checked[dateIndex] = `${date} 00:00`);
    }

    setFinanceReportFiltersDateSelectedOption = (option: any) => {
        this.financeReportFiltersDateSelectedOption = option;
        const exist = this.financeReportFiltersDateToSend[option[2]].find((exist: any) => exist.name === option[1]);
        exist ? this.setDateFromTo(exist.checked[0], exist.checked[1]) : this.setDateFromTo('', '');
    }

    setFinanceReportFilters = (data: any) => {
        this.financeReportFilters = data;

        this.checkedFilters = data.map((filter: any) => filter.name !== 'date_filters' &&
            filter.filters.map((filters: any) => filters.checkboxes && filters.checkboxes.map(() => true))).filter((data: any) => data && data);

        const date = data.filter((filter: any) => filter.name === 'date_filters')[0].filters[0];
        this.financeReportFiltersDateSelectedOption = [date.display_name, date.name, date.filter_key];
    }

    setRightTableFinanceReport = (data: any) => {
        this.rightTableCheckbox = Array(data.length).fill({ checked: false, fk_id: -1 });
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, fk_id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTableFinanceReport = data.concat(moreRows);
        this.setRightTableFinanceReportDownloadCSV(data);
    }

    setLeftTableFinanceReport = (data: any, dontCheckRightTable?: boolean) => {
        this.leftTableCheckbox = Array(data.length).fill({ checked: false });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTableFinanceReport = data.concat(moreRows);
        !dontCheckRightTable && this.setRightTableSelectedItems();
        this.setLeftTableFinanceReportDownloadCSV(this.leftTableFinanceReport);
    }

    setAllFinanceReport = (data: any) => {
        this.allFinanceReport = data;
        data && data.length > 0 && data[0][this.selectedLeftTableTab] && this.setLeftTableFinanceReport(data[0][this.selectedLeftTableTab]);
        data && data.length > 1 && data[1][this.selectedRightTableTab] && this.setRightTableFinanceReport(data[1][this.selectedRightTableTab])
    }

    fetchFilteredFinanceReport = (body: any) => {
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
        const body = this.leftTableCheckbox.filter((data: any) => data.checked)
            .map((data: any) => ({
                attribution: data.item.attribution, attribution_id: data.item.attribution_id, fk_branch_id: data.item.fk_branch_id,
                fk_institution_id: data.item.fk_institution_id, fk_trend_coordinator_id: data.item.fk_trend_coordinator_id,
                payment_method: data.item.payment_method, amount: data.item.expense_sum,
                fk_bank_account_id: data.item.fk_bank_account_id, payment_status: 'טיוטה'
            }));

        body.length > 0 && Fetch.Post('finance_report?pay=true', body)
            .then((res) => { this.changeExpenseMessage(res.message.value); this.resetCheckbox(); })
            .catch(err => console.error(err))
    }
}

export default new FinanceReportStore();