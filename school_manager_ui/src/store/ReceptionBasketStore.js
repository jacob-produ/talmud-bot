import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class ReceptionBasketStore {
    constructor() {
        makeAutoObservable(this);
    }

    allReceptionBasket = null;
    leftTableReceptionBasket = Array(10).fill('');
    rightTableReceptionBasket = Array(10).fill('');
    receptionBasketFilters = [];
    receptionBasketFiltersToSend = { income_filters: [] }; //, expense_filters: [], student_filters: []
    // receptionBasketFiltersDateToSend = {
    //     expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
    //     income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
    //     student_filters: []
    // };
    receptionBasketFiltersDateSelectedOption = [];
    selectedLeftTableTab = 'donations';
    selectedRightTableTab = 'institution';
    leftTableSearch = '';
    rightTableSearch = '';
    // dateFrom = '';
    // dateTo = '';
    leftTableHeight = 0;
    rightTableHeight = 0;
    leftTableCheckbox = [];
    rightTableCheckbox = [];
    rightTableSelectedItems = [];
    checkedFilters = [];
    generalLists = [];
    bankAccount = [];
    trendCoordinator = [];

    setBankAccount = (value) => {
        this.bankAccount = value;
    }

    setTrendCoordinator = (value) => {
        this.trendCoordinator = value;
    }

    print = async (onlyShown) => {
        let body = [];
        onlyShown && this.allReceptionBasket[0][this.selectedLeftTableTab].map(item => item.is_printable && (body = [...body, item.income_id]));
        // Object.values(this.allReceptionBasket[0]).map(tab => tab.map(item => item.is_printable && (body = [...body, item.expense_id])));

        return await this.fetchPrint(onlyShown, body);
    }

    delete = (item, tableIndex) => {
        if (tableIndex === 0) {
            this.fetchDeleteIncome(item.income_id, {})
                .then((err) => {
                    if (!err) {
                        this.deleteSelectedItem(item, tableIndex);
                    }
                })
        }
        if (tableIndex === 1) {
            let body = [];
            this.leftTableReceptionBasket.map((leftTableItem) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                (body = [...body, leftTableItem.income_id]))
            this.fetchDeleteIncome(null, body)
                .then((err) => {
                    if (!err) {
                        this.leftTableReceptionBasket.map((leftTableItem) =>
                            item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                            this.deleteSelectedItem(leftTableItem, tableIndex))
                    }
                })
        }
    }

    deleteSelectedItem = (item, tableIndex) => {
        const data = this.leftTableReceptionBasket.filter(data => data !== item);
        this.setLeftTableReceptionBasket(data, true);
        this.allReceptionBasket[tableIndex][this.selectedLeftTableTab] = this.allReceptionBasket[tableIndex][this.selectedLeftTableTab]?.filter(leftItem => leftItem !== item);
    }

    checkIncome = (data, item, tableIndex, index, position, chengePosition) => {
        let leftTable = this.leftTableReceptionBasket;
        let body = {};
        body[position] = data;
        chengePosition && (position = chengePosition);
        if (tableIndex === 0)
            (position !== 'is_printable' || (position === 'is_printable' && this.checkIsPrintAllow(item))) &&
                this.fetchEditIncome(item.income_id, body)
                    .then((err) => {
                        if (!err) {
                            this.changeLeftTableReceptionBasket(leftTable, index, position, data);
                        }
                    })
        else if (tableIndex === 1)
            this.leftTableReceptionBasket.map((leftTableItem, index) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                (position !== 'is_printable' || (position === 'is_printable' && this.checkIsPrintAllow(leftTableItem))) &&
                this.fetchEditIncome(leftTableItem.income_id, body)
                    .then((err) => {
                        if (!err) {
                            this.changeLeftTableReceptionBasket(leftTable, index, position, data);
                        }
                    })
            )
    }

    checkIsPrintAllow = (item) => {
        this.leftTableReceptionBasket = this.leftTableReceptionBasket.map(leftBasket => {
            leftBasket === item && (delete leftBasket['show_error']);
            return leftBasket;
        })
        if (!item.for_month || item.for_month === 0) {
            this.leftTableReceptionBasket = this.leftTableReceptionBasket.map(leftBasket => {
                leftBasket === item && (leftBasket['show_error'] = true);
                return leftBasket;
            })
            return false
        }
        return true;
    }

    changeLeftTableReceptionBasket = (leftTable, index, position, data) => {
        leftTable[index][position] = data;
        this.leftTableReceptionBasket = [...leftTable];
    }

    changeCheckDate = (date, item, tableIndex, index) => {
        this.checkIncome(date, item, tableIndex, index, 'check_date');
    }

    changeForMonth = (date, item, tableIndex, index) => {
        this.checkIncome(date, item, tableIndex, index, 'for_month');
    }

    changeCheckSum = (sum, item, tableIndex, index) => {
        this.checkIncome(sum, item, tableIndex, index, 'amount', 'expense_sum');
    }

    changePaymentMethod = (paymentMethod, item, tableIndex, index) => {
        this.checkIncome(paymentMethod, item, tableIndex, index, 'method');
    }

    changeCheckbox = (checked, item, tableIndex, index) => {
        this.checkIncome(checked, item, tableIndex, index, 'is_printable');
    }

    changeBankAccountId = (id, item, tableIndex, index) => {
        this.checkIncome(id, item, tableIndex, index, 'fk_bank_account_id');
    }

    changeTrendCoordinatorId = (id, item, tableIndex, index) => {
        this.checkIncome(id, item, tableIndex, index, 'fk_trend_coordinator_id');
    }

    afterLeftTableUpdate = () => {
        this.rightTableReceptionBasket = this.rightTableReceptionBasket.map((rightTableItem, index) => {
            if (typeof rightTableItem === 'object' && rightTableItem !== null) {
                const countLeftTableWithSameFkId = this.leftTableReceptionBasket.filter(leftTableItem => !leftTableItem.deleted &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
                const countLeftTableWithSameFkIdToPrint = this.leftTableReceptionBasket.filter(leftTableItem =>
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                    leftTableItem.is_printable).length;
                this.rightTableReceptionBasket[index][`all_selected`] = countLeftTableWithSameFkId === 0 ? false :
                    countLeftTableWithSameFkId === countLeftTableWithSameFkIdToPrint;
                this.rightTableReceptionBasket[index][`print_${this.selectedLeftTableTab}_sum`] = countLeftTableWithSameFkIdToPrint;
                this.rightTableReceptionBasket[index][`${this.selectedLeftTableTab}_sum`] = this.leftTableReceptionBasket.filter(leftTableItem =>
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
            }
            return rightTableItem;
        })
    }

    setGeneralLists = (value) => {
        this.generalLists = value;
    }

    setCheckedFilters = (checkbox) => {
        this.checkedFilters = checkbox;
    }

    setRightTableSelectedItems = (checked, index, item) => {
        let tableSelectedItems = this.rightTableSelectedItems;
        if (item) {
            // this.leftTableSearch = '';
            tableSelectedItems[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableSelectedItems = [...tableSelectedItems];
        }

        const haveFilter = tableSelectedItems.some(exist => exist.checked);
        const data = this.leftTableSearch.trim() === '' ? this.allReceptionBasket[0][this.selectedLeftTableTab] : this.leftTableReceptionBasket;
        if (haveFilter) {
            let filteredData = [];
            tableSelectedItems.map(check => check.checked && (filteredData = [...filteredData, ...data.filter(rightItem =>
                rightItem[`fk_${this.selectedRightTableTab}_id`] ? rightItem[`fk_${this.selectedRightTableTab}_id`] === check.fk_id : true)]));
            filteredData = filteredData.filter((newSet => ({ identity }) => !newSet.has(identity) && newSet.add(identity))(new Set()));
            this.setLeftTableReceptionBasket(filteredData, true);
        }
        else
            this.setLeftTableReceptionBasket(data, true);
    }

    setLeftTableHeight = (height) => {
        this.leftTableHeight = height;
    }

    setRightTableHeight = (height) => {
        this.rightTableHeight = height;
    }

    // setDateFromTo = (from, to) => {
    //     from ? (this.dateFrom = from.slice(0, 10).split('/').reverse().join('-')) : from === '' && (this.dateFrom = '');
    //     to ? (this.dateTo = to.slice(0, 10).split('/').reverse().join('-')) : to === '' && (this.dateTo = '');
    // }

    setTableSearch = (tableIndex, value) => {
        if (tableIndex === 0) {
            this.leftTableSearch = value;
            const filteredSearch = (this.allReceptionBasket[tableIndex])[this.selectedLeftTableTab].filter(search =>
                search.identity.includes(value) || search.full_name.toLowerCase().includes(value.toLowerCase()) ||
                (search.for_month && search.for_month.includes(value)) || search.amount.toString().includes(value) ||
                search.method.includes(value));
            this.setLeftTableReceptionBasket(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = (this.allReceptionBasket[tableIndex])[this.selectedRightTableTab].filter(search =>
                search.name.toLowerCase().includes(value.toLowerCase()) || search.expense_sum.toString().includes(value) ||
                search.balance_total.toString().includes(value));
            this.setRightTableReceptionBasket(filteredSearch);
        }
    }

    setSelectedTableTab = (tableIndex, tab) => {
        if (tableIndex === 0 && this.selectedLeftTableTab !== tab) {
            this.leftTableSearch = '';
            this.selectedLeftTableTab = tab;
            this.setLeftTableReceptionBasket((this.allReceptionBasket[tableIndex])[tab]);
        }
        else if (tableIndex === 1 && this.selectedRightTableTab !== tab) {
            this.rightTableSearch = '';
            this.selectedRightTableTab = tab;
            this.setRightTableReceptionBasket((this.allReceptionBasket[tableIndex])[tab]);
            this.setRightTableSelectedItems();
        }
    }

    setReceptionBasketFiltersToSend = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex, fill) => {
        fill === 'checkAll' && (this.ReceptionBasketFiltersToSend = { income_filters: [] }); //, expense_filters: [], student_filters: [] 

        fill === 'unCheckAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => false))) :
            fill === 'checkAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => true))) :
                (this.checkedFilters[titleIndex][filterIndex][checkboxIndex] = !this.checkedFilters[titleIndex][filterIndex][checkboxIndex]);

        fill === 'unCheckAll' ?
            this.receptionBasketFilters.map(filters =>
                filters.name !== 'date_filters' && this.receptionBasketFiltersToSend[filters.name].map(filter =>
                    filter.checked = [])) :
            fill === 'checkAll' ?
                this.receptionBasketFilters.map(filters =>
                    filters.name !== 'date_filters' &&
                    filters.filters.map(filter =>
                        this.receptionBasketFiltersToSend[filters.name] = [...this.receptionBasketFiltersToSend[filters.name], { name: filter.name, checked: filter.checkboxes }])) :
                this.receptionBasketFiltersToSend[titleName].map(filter =>
                    filter.name === name && (filter.checked.some(exist => exist === checked) ?
                        (filter.checked = filter.checked.filter(value => value !== checked)) :
                        (filter.checked = [...filter.checked, checked])));
    }

    // setReceptionBasketFiltersDateToSend = (date, dateIndex, fill) => {
    //     const selectedOption = this.peceptionBasketFiltersDateSelectedOption;
    //     let existIndex = this.receptionBasketFiltersDateToSend[selectedOption[2]].findIndex(exist => exist.name === selectedOption[1]);

    //     if (existIndex === -1) {
    //         existIndex = this.receptionBasketFiltersDateToSend[selectedOption[2]].length;
    //         this.receptionBasketFiltersDateToSend[selectedOption[2]] = [...this.receptionBasketFiltersDateToSend[selectedOption[2]],
    //         { name: selectedOption[1], checked: ['', ''] }]
    //     }

    //     fill === 'clear' ?
    //         this.receptionBasketFiltersDateToSend = {
    //             expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
    //             income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }], student_filters: []
    //         } :
    //         (this.receptionBasketFiltersDateToSend[selectedOption[2]][existIndex]).checked[dateIndex] = `${date} 00:00`;
    // }

    // setReceptionBasketFiltersDateSelectedOption = (option) => {
    //     this.receptionBasketFiltersDateSelectedOption = option;
    //     const exist = this.receptionBasketFiltersDateToSend[option[2]].find(exist => exist.name === option[1]);
    //     exist ? this.setDateFromTo(exist.checked[0], exist.checked[1]) : this.setDateFromTo('', '');
    // }

    setReceptionBasketFilters = (data) => {
        this.receptionBasketFilters = data;

        this.checkedFilters = data.map(filter => filter.name !== 'date_filters' &&
            filter.filters.map(filters => filters.checkboxes && filters.checkboxes.map(() => true))).filter(data => data && data);

        // const date = data.filter(filter => filter.name === 'date_filters')[0]?.filters[0];
        // this.receptionBasketFiltersDateSelectedOption = [date.display_name, date.name, date.filter_key];
    }

    setRightTableReceptionBasket = (data) => {
        this.rightTableCheckbox = Array(data.length).fill({ checked: false, fk_id: -1 });
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, fk_id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTableReceptionBasket = data.concat(moreRows);
    }

    setLeftTableReceptionBasket = (data, dontCheckRightTable) => {
        this.leftTableCheckbox = data.map(item => ({ checked: item.is_printable, fk_id: -1 }));
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTableReceptionBasket = data.concat(moreRows);
        !dontCheckRightTable && this.setRightTableSelectedItems();
    }

    setAllReceptionBasket = (data) => {
        data && data.length > 1 && Object.keys(data[1]).map(rightTableTabName =>
            data[1][rightTableTabName].map((rightTableItem, index) =>
                Object.keys(data[0]).map(leftTableTabName =>
                (data[1][rightTableTabName][index][`${leftTableTabName}_sum`] = data[0][leftTableTabName].filter(leftTableItem =>
                    rightTableItem[`fk_${rightTableTabName}_id`] === leftTableItem[`fk_${rightTableTabName}_id`]
                ).length))
            )
        )

        this.allReceptionBasket = data;
        data && data.length > 0 && data[0][this.selectedLeftTableTab] && this.setLeftTableReceptionBasket(data[0][this.selectedLeftTableTab]);
        data && data.length > 1 && data[1][this.selectedRightTableTab] && this.setRightTableReceptionBasket(data[1][this.selectedRightTableTab])
    }

    fetchFilteredReceptionBasket = (body) => {
        this.setAllReceptionBasket(null);
        Fetch.Post('reception_basket', body)
            .then(res => this.setAllReceptionBasket(res))
            .catch(err => console.error(err))
    }

    fetchReceptionBasketFilters = async () => {
        return await Fetch.Get('reception_basket_filters')
            .then(res => this.setReceptionBasketFilters(res))
            .then(() => {
                this.fetchGeneralLists();
                this.fetchBankAccount();
                this.fetchTrendCoordinator();
            })
            .catch(err => console.error(err))
    }

    fetchGeneralLists = () => {
        Fetch.Get('general_lists')
            .then(res => this.setGeneralLists(res))
            .catch(err => console.error(err))
    }

    fetchEditIncome = async (id, body) => {
        return await Fetch.Put(`income/${id}`, body)
            .then(res => res.error)
            .catch(err => console.error(err))
    }

    fetchDeleteIncome = async (id, body) => {
        return await Fetch.Delete(`income${id ? `/${id}` : ''}`, body)
            .then(res => res.error)
            .catch(err => console.error(err))
    }

    fetchPrint = async (onlyShown) => {
        let body = [];
        onlyShown && this.allReceptionBasket[0][this.selectedLeftTableTab].map(item => item.is_printable && (body = [...body, item.expense_id]));

        if (!(onlyShown && body.length === 0)) {
            return await Fetch.Post('income/print_payment', body, true)
                .catch(err => console.error(err))
        }
    }

    fetchBankAccount = () => {
        Fetch.Get('bank_account?verbose=true')
            .then(res => this.setBankAccount(res))
            .catch(err => console.error(err))
    }

    fetchTrendCoordinator = () => {
        Fetch.Get('trend_coordinator')
            .then(res => this.setTrendCoordinator(res))
            .catch(err => console.error(err))
    }
}

export default new ReceptionBasketStore();