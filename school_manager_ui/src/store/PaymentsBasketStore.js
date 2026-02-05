import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class PaymentsBasketStore {
    constructor() {
        makeAutoObservable(this);
    }

    allPaymentsBasket = null;
    leftTablePaymentsBasket = Array(10).fill('');
    rightTablePaymentsBasket = Array(10).fill('');
    paymentsBasketFilters = [];
    paymentsBasketFiltersToSend = { expense_filters: [], student_filters: [] }; //income_filters: [],
    // paymentsBasketFiltersDateToSend = {
    //     expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
    //     income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
    //     student_filters: []
    // };
    paymentsBasketFiltersDateSelectedOption = [];
    selectedLeftTableTab = 'student';
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
    mergedCheckbox = []

    changeMergedCheckbox = (checked, id, clear) => {
        if (clear)
            this.mergedCheckbox = [];
        else if (checked)
            this.mergedCheckbox = [...this.mergedCheckbox, id];
        else {
            const index = this.mergedCheckbox.indexOf(id);
            this.mergedCheckbox = [...this.mergedCheckbox.slice(0, index), ...this.mergedCheckbox.slice(index + 1, this.mergedCheckbox.length + 1)];
        }
    }

    setBankAccount = (value) => {
        this.bankAccount = value;
    }

    setTrendCoordinator = (value) => {
        this.trendCoordinator = value;
    }

    print = async (onlyShown) => {
        let body = [];
        onlyShown && this.allPaymentsBasket[0][this.selectedLeftTableTab].map(item => item.is_printable && (body = [...body, item.expense_id]));
        // Object.values(this.allPaymentsBasket[0]).map(tab => tab.map(item => item.is_printable && (body = [...body, item.expense_id])));

        return await this.fetchPrint(onlyShown, body);
    }

    delete = (item, tableIndex) => {
        if (tableIndex === 0) {
            this.fetchDeleteExpense(item.expense_id, {})
                .then((err) => {
                    if (!err) {
                        this.deleteSelectedItem(item, tableIndex);
                    }
                })
        }
        if (tableIndex === 1) {
            let body = [];
            this.leftTablePaymentsBasket.map((leftTableItem) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                (body = [...body, leftTableItem.expense_id]))
            this.fetchDeleteExpense(null, body)
                .then((err) => {
                    if (!err) {
                        this.leftTablePaymentsBasket.map((leftTableItem) =>
                            item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                            this.deleteSelectedItem(leftTableItem, tableIndex))
                    }
                })
        }
    }

    deleteSelectedItem = (item, tableIndex) => {
        const data = this.leftTablePaymentsBasket.filter(data => data !== item);
        this.setLeftTablePaymentsBasket(data, true);
        this.allPaymentsBasket[tableIndex][this.selectedLeftTableTab] = this.allPaymentsBasket[tableIndex][this.selectedLeftTableTab]?.filter(leftItem => leftItem !== item);
    }

    checkExpence = (data, item, tableIndex, index, position, chengePosition) => {
        let leftTable = this.leftTablePaymentsBasket;
        let body = {};
        body[position] = data;
        chengePosition && (position = chengePosition);
        if (tableIndex === 0)
            (position !== 'is_printable' || (position === 'is_printable' && this.checkIsPrintAllow(item))) &&
                this.fetchEditExpense(item.expense_id, body)
                    .then((err) => {
                        if (!err) {
                            this.changeLeftTablePaymentsBasket(leftTable, index, position, data);
                        }
                    })
        else if (tableIndex === 1)
            this.leftTablePaymentsBasket.map((leftTableItem, index) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                (position !== 'is_printable' || (position === 'is_printable' && this.checkIsPrintAllow(leftTableItem))) &&
                this.fetchEditExpense(leftTableItem.expense_id, body)
                    .then((err) => {
                        if (!err) {
                            this.changeLeftTablePaymentsBasket(leftTable, index, position, data);
                        }
                    })
            )
    }

    checkIsPrintAllow = (item) => {
        this.leftTablePaymentsBasket = this.leftTablePaymentsBasket.map(leftBasket => {
            leftBasket === item && (delete leftBasket['show_error']);
            return leftBasket;
        })
        if (((!item.expense_sum || item.expense_sum === 0) ||
            !item.payment_method || (!item.for_month || item.for_month === 0) ||
            (item.payment_method === 'שיק' && (!item.transmission_date || item.transmission_date === 0)))) {
            this.leftTablePaymentsBasket = this.leftTablePaymentsBasket.map(leftBasket => {
                leftBasket === item && (leftBasket['show_error'] = true);
                return leftBasket;
            })
            return false
        }
        return true;
    }

    changeLeftTablePaymentsBasket = (leftTable, index, position, data) => {
        leftTable[index][position] = data;
        this.leftTablePaymentsBasket = [...leftTable];
    }

    changeCheckDate = (date, item, tableIndex, index) => {
        this.checkExpence(date, item, tableIndex, index, 'transmission_date');
    }

    changeForMonth = (date, item, tableIndex, index) => {
        this.checkExpence(date, item, tableIndex, index, 'for_month');
    }

    changeCheckSum = (sum, item, tableIndex, index) => {
        this.checkExpence(sum, item, tableIndex, index, 'amount', 'expense_sum');
    }

    changePaymentMethod = (paymentMethod, item, tableIndex, index) => {
        this.checkExpence(paymentMethod, item, tableIndex, index, 'payment_method');
    }

    changeCheckbox = (checked, item, tableIndex, index) => {
        this.checkExpence(checked, item, tableIndex, index, 'is_printable');
    }

    changeBankAccountId = (id, item, tableIndex, index) => {
        this.checkExpence(id, item, tableIndex, index, 'fk_bank_account_id');
    }

    changeTrendCoordinatorId = (id, item, tableIndex, index) => {
        this.checkExpence(id, item, tableIndex, index, 'fk_trend_coordinator_id');
    }

    afterLeftTableUpdate = () => {
        this.rightTablePaymentsBasket = this.rightTablePaymentsBasket.map((rightTableItem, index) => {
            if (typeof rightTableItem === 'object' && rightTableItem !== null) {
                const countLeftTableWithSameFkId = this.leftTablePaymentsBasket.filter(leftTableItem => !leftTableItem.deleted &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
                const countLeftTableWithSameFkIdToPrint = this.leftTablePaymentsBasket.filter(leftTableItem =>
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                    leftTableItem.is_printable).length;
                this.rightTablePaymentsBasket[index][`all_selected`] = countLeftTableWithSameFkId === 0 ? false :
                    countLeftTableWithSameFkId === countLeftTableWithSameFkIdToPrint;
                this.rightTablePaymentsBasket[index][`print_${this.selectedLeftTableTab}_sum`] = countLeftTableWithSameFkIdToPrint;
                this.rightTablePaymentsBasket[index][`${this.selectedLeftTableTab}_sum`] = this.leftTablePaymentsBasket.filter(leftTableItem =>
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
        const data = this.leftTableSearch.trim() === '' ? this.allPaymentsBasket[0][this.selectedLeftTableTab] : this.leftTablePaymentsBasket;
        if (haveFilter) {
            let filteredData = [];
            tableSelectedItems.map(check => check.checked && (filteredData = [...filteredData, ...data.filter(rightItem =>
                rightItem[`fk_${this.selectedRightTableTab}_id`] ? rightItem[`fk_${this.selectedRightTableTab}_id`] === check.fk_id : true)]));
            filteredData = filteredData.filter((newSet => ({ identity }) => !newSet.has(identity) && newSet.add(identity))(new Set()));
            this.setLeftTablePaymentsBasket(filteredData, true);
        }
        else
            this.setLeftTablePaymentsBasket(data, true);
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
            const filteredSearch = (this.allPaymentsBasket[tableIndex])[this.selectedLeftTableTab].filter(search =>
                search.identity.includes(value) || search.full_name.toLowerCase().includes(value.toLowerCase()) ||
                search.for_month.includes(value) || search.transmission_date.includes(value) || search.expense_sum.toString().includes(value) ||
                search.payment_method.toLowerCase().includes(value.toLowerCase()) || search.balance_total.toString().includes(value));
            this.setLeftTablePaymentsBasket(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = (this.allPaymentsBasket[tableIndex])[this.selectedRightTableTab].filter(search =>
                search.name.toLowerCase().includes(value.toLowerCase()) || search.expense_sum_total.includes(value) ||
                search.expense_sum.includes(value) || search.balance_total.toString().includes(value));
            this.setRightTablePaymentsBasket(filteredSearch);
        }
    }

    setSelectedTableTab = (tableIndex, tab) => {
        if (tableIndex === 0 && this.selectedLeftTableTab !== tab) {
            this.leftTableSearch = '';
            this.selectedLeftTableTab = tab;
            this.setLeftTablePaymentsBasket((this.allPaymentsBasket[tableIndex])[tab]);
        }
        else if (tableIndex === 1 && this.selectedRightTableTab !== tab) {
            this.rightTableSearch = '';
            this.selectedRightTableTab = tab;
            this.setRightTablePaymentsBasket((this.allPaymentsBasket[tableIndex])[tab]);
            this.setRightTableSelectedItems();
        }
    }

    setPaymentsBasketFiltersToSend = (titleName, name, checked, titleIndex, filterIndex, checkboxIndex, fill) => {
        fill === 'checkAll' && (this.paymentsBasketFiltersToSend = { expense_filters: [], student_filters: [] }); //, income_filters: []

        fill === 'unCheckAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => false))) :
            fill === 'checkAll' ? this.checkedFilters = this.checkedFilters.map(checkboxes => checkboxes.map(checkbox => checkbox.map(() => true))) :
                (this.checkedFilters[titleIndex][filterIndex][checkboxIndex] = !this.checkedFilters[titleIndex][filterIndex][checkboxIndex]);

        fill === 'unCheckAll' ?
            this.paymentsBasketFilters.map(filters =>
                filters.name !== 'date_filters' && this.paymentsBasketFiltersToSend[filters.name].map(filter =>
                    filter.checked = [])) :
            fill === 'checkAll' ?
                this.paymentsBasketFilters.map(filters =>
                    filters.name !== 'date_filters' &&
                    filters.filters.map(filter =>
                        this.paymentsBasketFiltersToSend[filters.name] = [...this.paymentsBasketFiltersToSend[filters.name], { name: filter.name, checked: filter.checkboxes }])) :
                this.paymentsBasketFiltersToSend[titleName].map(filter =>
                    filter.name === name && (filter.checked.some(exist => exist === checked) ?
                        (filter.checked = filter.checked.filter(value => value !== checked)) :
                        (filter.checked = [...filter.checked, checked])));
    }

    // setPaymentsBasketFiltersDateToSend = (date, dateIndex, fill) => {
    //     const selectedOption = this.pPaymentsBasketFiltersDateSelectedOption;
    //     let existIndex = this.paymentsBasketFiltersDateToSend[selectedOption[2]].findIndex(exist => exist.name === selectedOption[1]);

    //     if (existIndex === -1) {
    //         existIndex = this.paymentsBasketFiltersDateToSend[selectedOption[2]].length;
    //         this.paymentsBasketFiltersDateToSend[selectedOption[2]] = [...this.paymentsBasketFiltersDateToSend[selectedOption[2]],
    //         { name: selectedOption[1], checked: ['', ''] }]
    //     }

    //     fill === 'clear' ?
    //         this.paymentsBasketFiltersDateToSend = {
    //             expense_filters: [{ name: 'expense_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }],
    //             income_filters: [{ name: 'income_date', checked: [`01/01/${new Date().getFullYear()} 00:00`, ''] }], student_filters: []
    //         } :
    //         (this.paymentsBasketFiltersDateToSend[selectedOption[2]][existIndex]).checked[dateIndex] = `${date} 00:00`;
    // }

    // setPaymentsBasketFiltersDateSelectedOption = (option) => {
    //     this.paymentsBasketFiltersDateSelectedOption = option;
    //     const exist = this.paymentsBasketFiltersDateToSend[option[2]].find(exist => exist.name === option[1]);
    //     exist ? this.setDateFromTo(exist.checked[0], exist.checked[1]) : this.setDateFromTo('', '');
    // }

    setPaymentsBasketFilters = (data) => {
        this.paymentsBasketFilters = data;

        this.checkedFilters = data.map(filter => filter.name !== 'date_filters' &&
            filter.filters.map(filters => filters.checkboxes && filters.checkboxes.map(() => true))).filter(data => data && data);

        // const date = data.filter(filter => filter.name === 'date_filters')[0]?.filters[0];
        // this.paymentsBasketFiltersDateSelectedOption = [date.display_name, date.name, date.filter_key];
    }

    setRightTablePaymentsBasket = (data) => {
        this.rightTableCheckbox = Array(data.length).fill({ checked: false, fk_id: -1 });
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, fk_id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTablePaymentsBasket = data.concat(moreRows);
    }

    setLeftTablePaymentsBasket = (data, dontCheckRightTable) => {
        this.leftTableCheckbox = data.map(item => ({ checked: item.is_printable, fk_id: -1 }));
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTablePaymentsBasket = data.concat(moreRows);
        !dontCheckRightTable && this.setRightTableSelectedItems();
    }

    setAllPaymentsBasket = (data) => {
        data && data.length > 1 && Object.keys(data[1]).map(rightTableTabName =>
            data[1][rightTableTabName].map((rightTableItem, index) =>
                Object.keys(data[0]).map(leftTableTabName =>
                (data[1][rightTableTabName][index][`${leftTableTabName}_sum`] = data[0][leftTableTabName].filter(leftTableItem =>
                    rightTableItem[`fk_${rightTableTabName}_id`] === leftTableItem[`fk_${rightTableTabName}_id`]
                ).length))
            )
        )

        this.allPaymentsBasket = data;
        data && data.length > 0 && data[0][this.selectedLeftTableTab] && this.setLeftTablePaymentsBasket(data[0][this.selectedLeftTableTab]);
        data && data.length > 1 && data[1][this.selectedRightTableTab] && this.setRightTablePaymentsBasket(data[1][this.selectedRightTableTab])
    }

    fetchFilteredPaymentsBasket = (body) => {
        this.setAllPaymentsBasket(null);
        Fetch.Post('payment_basket', body)
            .then(res => this.setAllPaymentsBasket(res))
            .catch(err => console.error(err))
    }

    fetchPaymentsBasketFilters = async () => {
        return await Fetch.Get('finance_report/filters?payment_basket=true')
            .then(res => this.setPaymentsBasketFilters(res))
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

    fetchEditExpense = async (id, body) => {
        return await Fetch.Put(`expense/${id}`, body)
            .then(res => res.error)
            .catch(err => console.error(err))
    }

    fetchDeleteExpense = async (id, body) => {
        return await Fetch.Delete(`expense${id ? `/${id}` : ''}`, body)
            .then(res => res.error)
            .catch(err => console.error(err))
    }

    fetchPrint = async (onlyShown,checkConsolidation) => {
        let body = [];
        onlyShown && this.allPaymentsBasket[0][this.selectedLeftTableTab].map(item => item.is_printable && (body = [...body, item.expense_id]));
        console.log(checkConsolidation);

        let header = checkConsolidation?`expense/print_payment?grouping=${checkConsolidation}`:'expense/print_payment'

        if (!(onlyShown && body.length === 0)) {
            return await Fetch.Post(header, body, true)
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

    fetchMerge = () => {
        Fetch.Post('expense/merge_payment', this.mergedCheckbox)
            .then(res => {
                this.changeMergedCheckbox(null, null, true);
                this.fetchFilteredPaymentsBasket(this.paymentsBasketFiltersToSend);
            })
            .catch(err => console.error(err))
    }

    fetchSplit = (merged_number) => {
        let expense_id = [];
        this.leftTablePaymentsBasket.forEach(item => {
            if (item?.merged_printing_number === merged_number)
                expense_id = [...expense_id, item.expense_id];
        })

        Fetch.Post('expense/split_payment', expense_id)
            .then(res => {
                this.fetchFilteredPaymentsBasket(this.paymentsBasketFiltersToSend);
            })
            .catch(err => console.error(err))
    }
}

export default new PaymentsBasketStore();