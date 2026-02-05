import { makeAutoObservable } from 'mobx';
import * as Fetch from '../../Fetch';

class PeriodicReceptionStore {
    constructor() {
        makeAutoObservable(this);
    }
    allPeriodicReception: any = null;
    leftTablePeriodicReception: any = Array(10).fill('');
    rightTablePeriodicReception: any = Array(10).fill('');
    periodicReceptionFilters: any = [];
    periodicReceptionFiltersToSend: any = { pr_filters: [] };
    periodicReceptionFiltersDateToSend: any = {
        pr_filters: [{ name: 'periodic_reception_create_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }]
    };
    periodicReceptionFiltersDateSelectedOption: any = [];
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
    checkIncome: boolean = true;
    checkExpense: boolean = true;

    changeCheckBox = (input: string, value: boolean) => {
        if (input === 'income') this.checkIncome = value;
        else if (input === 'expense') this.checkExpense = value;
        this.leftTableSearch = '';
        this.setLeftTablePeriodicReception(this.allPeriodicReception[0], true);
    }

    afterLeftTableUpdate = () => {
        const newRightTablePeriodicReception = this.rightTablePeriodicReception.map((rightTableItem: any, index: number) => {
            if (typeof rightTableItem === 'object' && rightTableItem !== null) {
                const countLeftTableWithSameFkId = this.leftTablePeriodicReception.filter((leftTableItem: any) => !leftTableItem.deleted &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
                const countLeftTableWithSameFkIdToPrint = this.leftTableCheckbox.filter((leftTableCheckboxItem: any) =>
                    leftTableCheckboxItem.item && leftTableCheckboxItem.checked &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableCheckboxItem.item[`fk_${this.selectedRightTableTab}_id`]).length;
                this.rightTablePeriodicReception[index][`all_selected`] = countLeftTableWithSameFkId === 0 ? false :
                    countLeftTableWithSameFkId === countLeftTableWithSameFkIdToPrint;
            }
            return rightTableItem;
        })
        this.rightTablePeriodicReception = newRightTablePeriodicReception;
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
        const data = this.leftTableSearch.trim() === '' ? this.allPeriodicReception[0] : this.leftTablePeriodicReception;
        if (haveFilter) {
            let filteredData: any = [];
            tableSelectedItems.map((check: any) => check.checked && (filteredData = [...filteredData, ...data.filter((rightItem: any) =>
                rightItem[`reception_${this.selectedRightTableTab}_id`] ? rightItem[`reception_${this.selectedRightTableTab}_id`] === check.fk_id : true)]));
            filteredData = filteredData.filter(((newSet: any) => (data: any) => !newSet.has(data.identity) && newSet.add(data.identity))(new Set()));
            this.setLeftTablePeriodicReception(filteredData, true);
        }
        else
            this.setLeftTablePeriodicReception(data, true);
    }

    setRightTableCheckbox = (checked?: boolean, index?: number, item?: any) => {
        let tableCheckbox = this.rightTableCheckbox;
        if (item && index) {
            // this.leftTableSearch = '';
            tableCheckbox[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableCheckbox = [...tableCheckbox];

            this.leftTableCheckbox = this.leftTablePeriodicReception.map((leftTableItem: any, index: number) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] ?
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

    setDateFromTo = (from: any, to?: any) => {
        from ? (this.dateFrom = from.slice(0, 10).split('/').reverse().join('-')) : from === '' && (this.dateFrom = '');
        to ? (this.dateTo = to.slice(0, 10).split('/').reverse().join('-')) : to === '' && (this.dateTo = '');
    }

    setTableSearch = (tableIndex: number, value: string) => {
        if (tableIndex === 0) {
            this.leftTableSearch = value;
            const filteredSearch = (this.allPeriodicReception[tableIndex]).filter((search: any) => search.identity?.includes(value) ||
                search.heb_attribution?.includes(value) || search.full_name?.toLowerCase()?.includes(value.toLowerCase()) ||
                search.payment_status?.includes(value) || search.amount?.toString()?.includes(value) || search.payment_method?.includes(value) ||
                (search.for_month?.slice(0, 10).split('-').reverse().join('/'))?.includes(value) ||
                (search.printing_date?.slice(0, 10).split('-').reverse().join('/'))?.includes(value) ||
                (search.reception_date?.slice(0, 10).split('-').reverse().join('/'))?.includes(value));
            this.setLeftTablePeriodicReception(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = (this.allPeriodicReception[tableIndex])[this.selectedRightTableTab].filter((search: any) =>
                search.name?.toLowerCase()?.includes(value.toLowerCase()) || search.balance?.toString()?.includes(value) ||
                search.balance_total?.toString()?.includes(value));
            this.setRightTablePeriodicReception(filteredSearch);
        }
    }

    setSelectedTableTab = (tableIndex: number, tab: string) => {
        if (tableIndex === 1 && this.selectedRightTableTab !== tab) {
            this.rightTableSearch = '';
            this.selectedRightTableTab = tab;
            this.setRightTablePeriodicReception((this.allPeriodicReception[tableIndex])[tab]);
            this.setRightTableSelectedItems();
        }
    }

    setPeriodicReceptionFiltersToSend = (titleName: any, name: any, checked: any, titleIndex: any, filterIndex: any, checkboxIndex: any, fill?: any) => {
        fill === 'checkAll' && (this.periodicReceptionFiltersToSend = { pr_filters: [] });

        fill === 'unCheckAll' ? this.checkedFilters = this.checkedFilters.map((checkboxes: any) => checkboxes.map((checkbox: any) => checkbox.map(() => false))) :
            fill === 'checkAll' ? this.checkedFilters = this.checkedFilters.map((checkboxes: any) => checkboxes.map((checkbox: any) => checkbox.map(() => true))) :
                titleIndex - 1 > -1 && (this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex] = !this.checkedFilters[titleIndex - 1][filterIndex][checkboxIndex]);

        fill === 'unCheckAll' ?
            this.periodicReceptionFilters.map((filters: any) =>
                filters.name !== 'date_filters' && this.periodicReceptionFiltersToSend[filters.name].map((filter: any) =>
                    filter.checked = [])) :
            fill === 'checkAll' ?
                this.periodicReceptionFilters.map((filters: any) =>
                    filters.name !== 'date_filters' &&
                    filters.filters.map((filter: any) =>
                        this.periodicReceptionFiltersToSend[filters.name] = [...this.periodicReceptionFiltersToSend[filters.name], { name: filter.name, checked: filter.checkboxes }])) :
                this.periodicReceptionFiltersToSend[titleName].map((filter: any) =>
                    filter.name === name && (filter.checked.some((exist: any) => exist === checked) ?
                        (filter.checked = filter.checked.filter((value: any) => value !== checked)) :
                        (filter.checked = [...filter.checked, checked])));
    }

    setPeriodicReceptionFiltersDateToSend = (date: any, dateIndex: any, fill?: any) => {
        const selectedOption = this.periodicReceptionFiltersDateSelectedOption;
        let existIndex = this.periodicReceptionFiltersDateToSend[selectedOption[2]].findIndex((exist: any) => exist.name === selectedOption[1]);

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

    setPeriodicReceptionFiltersDateSelectedOption = (option: any) => {
        this.periodicReceptionFiltersDateSelectedOption = option;
        const exist = this.periodicReceptionFiltersDateToSend[option[2]].find((exist: any) => exist.name === option[1]);
        exist ? this.setDateFromTo(exist.checked[0], exist.checked[1]) : this.setDateFromTo('', '');
    }

    setPeriodicReceptionFilters = (data: any) => {
        this.periodicReceptionFilters = data;

        this.checkedFilters = data.map((filter: any) => filter.name && filter.name !== 'date_filters' &&
            filter.filters.map((filters: any) => filters.checkboxes && filters.checkboxes.map(() => true))).filter((data: any) => data && data);

        const date = data[0].filters[0];
        this.periodicReceptionFiltersDateSelectedOption = [date.display_name, date.name, date.filter_key];
    }

    setRightTablePeriodicReception = (data: any) => {
        this.rightTableCheckbox = Array(data.length).fill({ checked: false, fk_id: -1 });
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, fk_id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTablePeriodicReception = data.concat(moreRows);
    }

    setLeftTablePeriodicReception = (data: any, dontCheckRightTable?: boolean) => {
        data = data.filter((row: any) => (this.checkIncome && row.amount >= 0) || (this.checkExpense && row.amount < 0))
        this.leftTableCheckbox = Array(data.length).fill({ checked: false });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTablePeriodicReception = data.concat(moreRows);
        !dontCheckRightTable && this.setRightTableSelectedItems();
    }

    setAllPeriodicReception = (data: any) => {
        data && data.length > 0 && (data[0] = Object.keys(data[0]).map(key => data[0][key]).flat());
        this.allPeriodicReception = data;

        data && data.length > 0 && this.setLeftTablePeriodicReception(data[0]);
        data && data.length > 1 && data[1][this.selectedRightTableTab] && this.setRightTablePeriodicReception(data[1][this.selectedRightTableTab])
    }

    fetchFilteredPeriodicReception = (body: any) => {
        body = {}; // need to check
        this.setAllPeriodicReception(null);
        Fetch.Post('periodic_reception_report', body)
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