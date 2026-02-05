import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class PeriodicReceptionStore {
    constructor() {
        makeAutoObservable(this);
    }

    allPeriodicReception = null;
    leftTablePeriodicReception = Array(10).fill('');
    rightTablePeriodicReception = Array(10).fill('');
    periodicReceptionFilters = [];
    periodicReceptionFiltersToSend = { pr_filters: [] };
    periodicReceptionFiltersDateToSend = {
        pr_filters: [{ name: 'periodic_reception_create_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }]
    };
    periodicReceptionFiltersDateSelectedOption = [];
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

    changeCheckBox = (input, value) => {
        if (input === 'income') this.checkIncome = value;
        else if (input === 'expense') this.checkExpense = value;
        this.leftTableSearch = '';
        this.setLeftTablePeriodicReception(this.allPeriodicReception[0], true);
    }

    afterLeftTableUpdate = () => {
        const newRightTablePeriodicReception = this.rightTablePeriodicReception.map((rightTableItem, index) => {
            if (typeof rightTableItem === 'object' && rightTableItem !== null) {
                const countLeftTableWithSameFkId = this.leftTablePeriodicReception.filter(leftTableItem => !leftTableItem.deleted &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
                const countLeftTableWithSameFkIdToPrint = this.leftTableCheckbox.filter(leftTableCheckboxItem =>
                    leftTableCheckboxItem.item && leftTableCheckboxItem.checked &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableCheckboxItem.item[`fk_${this.selectedRightTableTab}_id`]).length;
                this.rightTablePeriodicReception[index][`all_selected`] = countLeftTableWithSameFkId === 0 ? false :
                    countLeftTableWithSameFkId === countLeftTableWithSameFkIdToPrint;
            }
            return rightTableItem;
        })
        this.rightTablePeriodicReception = newRightTablePeriodicReception;
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
        const data = this.leftTableSearch.trim() === '' ? this.allPeriodicReception[0] : this.leftTablePeriodicReception;
        if (haveFilter) {
            let filteredData = [];
            tableSelectedItems.map(check => check.checked && (filteredData = [...filteredData, ...data.filter(rightItem =>
                rightItem[`reception_${this.selectedRightTableTab}_id`] ? rightItem[`reception_${this.selectedRightTableTab}_id`] === check.fk_id : true)]));
            filteredData = filteredData.filter((newSet => ({ identity }) => !newSet.has(identity) && newSet.add(identity))(new Set()));
            this.setLeftTablePeriodicReception(filteredData, true);
        }
        else
            this.setLeftTablePeriodicReception(data, true);
    }

    setRightTableCheckbox = (checked, index, item) => {
        let tableCheckbox = this.rightTableCheckbox;
        if (item) {
            // this.leftTableSearch = '';
            tableCheckbox[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableCheckbox = [...tableCheckbox];

            this.leftTableCheckbox = this.leftTablePeriodicReception.map((leftTableItem, index) =>
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
            const filteredSearch = (this.allPeriodicReception[tableIndex]).filter(search => search.identity?.includes(value) ||
                search.heb_attribution?.includes(value) || search.full_name?.toLowerCase()?.includes(value.toLowerCase()) ||
                search.payment_status?.includes(value) || search.amount?.toString()?.includes(value) || search.payment_method?.includes(value) ||
                (search.for_month?.slice(0, 10).split('-').reverse().join('/'))?.includes(value) ||
                (search.printing_date?.slice(0, 10).split('-').reverse().join('/'))?.includes(value) ||
                (search.reception_date?.slice(0, 10).split('-').reverse().join('/'))?.includes(value));
            this.setLeftTablePeriodicReception(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = (this.allPeriodicReception[tableIndex])[this.selectedRightTableTab].filter(search =>
                search.name?.toLowerCase()?.includes(value.toLowerCase()) || search.balance?.toString()?.includes(value) ||
                search.balance_total?.toString()?.includes(value));
            this.setRightTablePeriodicReception(filteredSearch);
        }
    }

    setSelectedTableTab = (tableIndex, tab) => {
        if (tableIndex === 1 && this.selectedRightTableTab !== tab) {
            this.rightTableSearch = '';
            this.selectedRightTableTab = tab;
            this.setRightTablePeriodicReception((this.allPeriodicReception[tableIndex])[tab]);
            this.setRightTableSelectedItems();
        }
    }

    setPeriodicReceptionFiltersToSend = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex, fill) => {
        fill === 'checkAll' && (this.periodicReceptionFiltersToSend = { pr_filters: [] });

        fill === 'unCheckAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => false))) :
            fill === 'checkAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => true))) :
                titleIndex - 1 > -1 && (this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex] = !this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex]);

        fill === 'unCheckAll' ?
            this.periodicReceptionFilters.map(filters =>
                filters.name !== 'date_filters' && this.periodicReceptionFiltersToSend[filters.name].map(filter =>
                    filter.checked = [])) :
            fill === 'checkAll' ?
                this.periodicReceptionFilters.map(filters =>
                    filters.name !== 'date_filters' &&
                    filters.filters.map(filter =>
                        this.periodicReceptionFiltersToSend[filters.name] = [...this.periodicReceptionFiltersToSend[filters.name], { name: filter.name, checked: filter.checkboxes }])) :
                this.periodicReceptionFiltersToSend[titleName].map(filter =>
                    filter.name === name && (filter.checked.some(exist => exist === checked) ?
                        (filter.checked = filter.checked.filter(value => value !== checked)) :
                        (filter.checked = [...filter.checked, checked])));
    }

    setPeriodicReceptionFiltersDateToSend = (date, dateIndex, fill) => {
        const selectedOption = this.periodicReceptionFiltersDateSelectedOption;
        let existIndex = this.periodicReceptionFiltersDateToSend[selectedOption[2]].findIndex(exist => exist.name === selectedOption[1]);

        if (existIndex === -1) {
            existIndex = this.periodicReceptionFiltersDateToSend[selectedOption[2]].length;
            this.periodicReceptionFiltersDateToSend[selectedOption[2]] = [...this.periodicReceptionFiltersDateToSend[selectedOption[2]],
            { name: selectedOption[1], checked: ['', ''] }]
        }

        fill === 'clear' ?
            this.periodicReceptionFiltersDateToSend = {
                pr_filters: [{ name: 'periodic_reception_create_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
            } :
            (this.periodicReceptionFiltersDateToSend[selectedOption[2]][existIndex]).checked[dateIndex] = `${date} 00:00`;
    }

    setPeriodicReceptionFiltersDateSelectedOption = (option) => {
        this.periodicReceptionFiltersDateSelectedOption = option;
        const exist = this.periodicReceptionFiltersDateToSend[option[2]].find(exist => exist.name === option[1]);
        exist ? this.setDateFromTo(exist.checked[0], exist.checked[1]) : this.setDateFromTo('', '');
    }

    setPeriodicReceptionFilters = (data) => {
        this.periodicReceptionFilters = data;

        this.checkedFilters = data.map(filter => filter.name && filter.name !== 'date_filters' &&
            filter.filters.map(filters => filters.checkboxes && filters.checkboxes.map(() => true))).filter(data => data && data);

        const date = data[0].filters[0];
        this.periodicReceptionFiltersDateSelectedOption = [date.display_name, date.name, date.filter_key];
    }

    setRightTablePeriodicReception = (data) => {
        this.rightTableCheckbox = Array(data.length).fill({ checked: false, fk_id: -1 });
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, fk_id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTablePeriodicReception = data.concat(moreRows);
    }

    setLeftTablePeriodicReception = (data, dontCheckRightTable) => {
        data = data.filter(row => (this.checkIncome && row.amount >= 0) || (this.checkExpense && row.amount < 0))
        this.leftTableCheckbox = Array(data.length).fill({ checked: false });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTablePeriodicReception = data.concat(moreRows);
        !dontCheckRightTable && this.setRightTableSelectedItems();
    }

    setAllPeriodicReception = (data) => {
        data && data.length > 0 && (data[0] = Object.keys(data[0]).map(key => data[0][key]).flat());
        this.allPeriodicReception = data;
        data && data.length > 0 && this.setLeftTablePeriodicReception(data[0]);
        data && data.length > 1 && data[1][this.selectedRightTableTab] && this.setRightTablePeriodicReception(data[1][this.selectedRightTableTab])
    }

    fetchFilteredPeriodicReception = (body) => {
        body = {}; // need to check
        this.setAllPeriodicReception(null);
        Fetch.Post('periodic_reception_report', body)
            .then(res => this.setAllPeriodicReception(res))
            .catch(err => console.error(err))
    }
    fetchNewRowData = (data) => {
        const convertedData = JSON.stringify(data)

        Fetch.Post('periodic_reception', convertedData)
            .then(res => this.setAllPeriodicReception(res))
            .catch(err => console.error(err))
    }

    fetchPeriodicReceptionFilters = async () => {
        return await !sessionStorage.getItem('reload') && Fetch.Get('periodic_reception_filters')
            .then(res => this.setPeriodicReceptionFilters(res))
            .catch(err => console.error(err))
    }

    resetCheckbox = () => {
        this.leftTableCheckbox = Array(this.leftTablePeriodicReception.length).fill({ checked: false });
    }
}

export default new PeriodicReceptionStore();