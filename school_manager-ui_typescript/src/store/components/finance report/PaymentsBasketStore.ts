import { makeAutoObservable } from 'mobx';
import * as Fetch from '../../Fetch';

class PaymentsBasketStore {
    constructor() {
        makeAutoObservable(this);
    }
    allPaymentsBasket: any = null;
    leftTablePaymentsBasket: any = Array(10).fill('');
    rightTablePaymentsBasket: any = Array(10).fill('');
    paymentsBasketFilters: any = [];
    paymentsBasketFiltersToSend: any = { expense_filters: [], student_filters: [] };
    paymentsBasketFiltersDateSelectedOption: any = [];
    selectedLeftTableTab: string = 'student';
    selectedRightTableTab: string = 'institution';
    leftTableSearch: string = '';
    rightTableSearch: string = '';
    leftTableHeight: number = 0;
    rightTableHeight: number = 0;
    leftTableCheckbox: any = [];
    rightTableCheckbox: any = [];
    rightTableSelectedItems: any = [];
    checkedFilters: any = [];
    generalLists: any = [];
    bankAccount: any = [];
    trendCoordinator: any = [];

    setBankAccount = (value: any) => {
        this.bankAccount = value;
    }

    setTrendCoordinator = (value: any) => {
        this.trendCoordinator = value;
    }

    // print = async (onlyShown: boolean) => {
    //     let body: any = [];
    //     onlyShown && this.allPaymentsBasket[0][this.selectedLeftTableTab].map((item: any) => item.is_printable && (body = [...body, item.expense_id]));
    //     // Object.values(this.allPaymentsBasket[0]).map(tab => tab.map(item => item.is_printable && (body = [...body, item.expense_id])));

    //     return await this.fetchPrint(onlyShown, body);
    // }

    delete = (item: any, tableIndex: number) => {
        if (tableIndex === 0) {
            this.fetchDeleteExpense(item.expense_id, {})
                .then((err) => {
                    if (!err) {
                        this.deleteSelectedItem(item, tableIndex);
                    }
                })
        }
        if (tableIndex === 1) {
            let body: any = [];
            this.leftTablePaymentsBasket.map((leftTableItem: any) =>
                item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                (body = [...body, leftTableItem.expense_id]))
            this.fetchDeleteExpense(null, body)
                .then((err) => {
                    if (!err) {
                        this.leftTablePaymentsBasket.map((leftTableItem: any) =>
                            item[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                            this.deleteSelectedItem(leftTableItem, tableIndex))
                    }
                })
        }
    }

    deleteSelectedItem = (item: any, tableIndex: number) => {
        const data = this.leftTablePaymentsBasket.filter((data: any) => data !== item);
        this.setLeftTablePaymentsBasket(data, true);
        this.allPaymentsBasket[tableIndex][this.selectedLeftTableTab] = this.allPaymentsBasket[tableIndex][this.selectedLeftTableTab]?.filter((leftItem: any) => leftItem !== item);
    }

    checkExpence = (data: any, item: any, tableIndex: any, index: any, position: any, chengePosition?: any) => {
        let leftTable = this.leftTablePaymentsBasket;
        let body: any = {};
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
            this.leftTablePaymentsBasket.map((leftTableItem: any, index: number) =>
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

    checkIsPrintAllow = (item: any) => {
        this.leftTablePaymentsBasket = this.leftTablePaymentsBasket.map((leftBasket: any) => {
            leftBasket === item && (delete leftBasket['show_error']);
            return leftBasket;
        })
        if (((!item.expense_sum || item.expense_sum === 0) ||
            !item.payment_method || (!item.for_month || item.for_month === 0) ||
            (item.payment_method === 'שיק' && (!item.check_date || item.check_date === 0)))) {
            this.leftTablePaymentsBasket = this.leftTablePaymentsBasket.map((leftBasket: any) => {
                leftBasket === item && (leftBasket['show_error'] = true);
                return leftBasket;
            })
            return false
        }
        return true;
    }

    changeLeftTablePaymentsBasket = (leftTable: any, index: number, position: any, data: any) => {
        leftTable[index][position] = data;
        this.leftTablePaymentsBasket = [...leftTable];
    }

    changeCheckDate = (date: any, item: any, tableIndex: number, index?: number) => {
        this.checkExpence(date, item, tableIndex, index, 'check_date');
    }

    changeForMonth = (date: any, item: any, tableIndex: number, index?: number) => {
        this.checkExpence(date, item, tableIndex, index, 'for_month');
    }

    changeCheckSum = (sum: any, item: any, tableIndex: number, index?: number) => {
        this.checkExpence(sum, item, tableIndex, index, 'amount', 'expense_sum');
    }

    changePaymentMethod = (paymentMethod: any, item: any, tableIndex: number, index?: number) => {
        this.checkExpence(paymentMethod, item, tableIndex, index, 'payment_method');
    }

    changeCheckbox = (checked: any, item: any, tableIndex: number, index?: number) => {
        this.checkExpence(checked, item, tableIndex, index, 'is_printable');
    }

    changeBankAccountId = (id: any, item: any, tableIndex: number, index: number) => {
        this.checkExpence(id, item, tableIndex, index, 'fk_bank_account_id');
    }

    changeTrendCoordinatorId = (id: any, item: any, tableIndex: number, index: number) => {
        this.checkExpence(id, item, tableIndex, index, 'fk_trend_coordinator_id');
    }

    afterLeftTableUpdate = () => {
        this.rightTablePaymentsBasket = this.rightTablePaymentsBasket.map((rightTableItem: any, index: number) => {
            if (typeof rightTableItem === 'object' && rightTableItem !== null) {
                const countLeftTableWithSameFkId = this.leftTablePaymentsBasket.filter((leftTableItem: any) => !leftTableItem.deleted &&
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
                const countLeftTableWithSameFkIdToPrint = this.leftTablePaymentsBasket.filter((leftTableItem: any) =>
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`] &&
                    leftTableItem.is_printable).length;
                this.rightTablePaymentsBasket[index][`all_selected`] = countLeftTableWithSameFkId === 0 ? false :
                    countLeftTableWithSameFkId === countLeftTableWithSameFkIdToPrint;
                this.rightTablePaymentsBasket[index][`print_${this.selectedLeftTableTab}_sum`] = countLeftTableWithSameFkIdToPrint;
                this.rightTablePaymentsBasket[index][`${this.selectedLeftTableTab}_sum`] = this.leftTablePaymentsBasket.filter((leftTableItem: any) =>
                    rightTableItem[`fk_${this.selectedRightTableTab}_id`] === leftTableItem[`fk_${this.selectedRightTableTab}_id`]).length;
            }
            return rightTableItem;
        })
    }

    setGeneralLists = (value: any) => {
        this.generalLists = value;
    }

    setCheckedFilters = (checkbox: any) => {
        this.checkedFilters = checkbox;
    }

    setRightTableSelectedItems = (checked?: boolean, index?: number, item?: any) => {
        let tableSelectedItems = this.rightTableSelectedItems;
        if (item && index) {
            // this.leftTableSearch = '';
            tableSelectedItems[index] = {
                checked, fk_id: item[`fk_${this.selectedRightTableTab}_id`]
            };
            this.rightTableSelectedItems = [...tableSelectedItems];
        }

        const haveFilter = tableSelectedItems.some((exist: any) => exist.checked);
        const data = this.leftTableSearch.trim() === '' ? this.allPaymentsBasket[0][this.selectedLeftTableTab] : this.leftTablePaymentsBasket;
        if (haveFilter) {
            let filteredData: any = [];
            tableSelectedItems.map((check: any) => check.checked && (filteredData = [...filteredData, ...data.filter((rightItem: any) =>
                rightItem[`fk_${this.selectedRightTableTab}_id`] ? rightItem[`fk_${this.selectedRightTableTab}_id`] === check.fk_id : true)]));
            filteredData = filteredData.filter(((newSet: any) => (data: any) => !newSet.has(data.identity) && newSet.add(data.identity))(new Set()));
            this.setLeftTablePaymentsBasket(filteredData, true);
        }
        else
            this.setLeftTablePaymentsBasket(data, true);
    }

    setLeftTableHeight = (height: number) => {
        this.leftTableHeight = height;
    }

    setRightTableHeight = (height: number) => {
        this.rightTableHeight = height;
    }

    // setDateFromTo = (from, to) => {
    //     from ? (this.dateFrom = from.slice(0, 10).split('/').reverse().join('-')) : from === '' && (this.dateFrom = '');
    //     to ? (this.dateTo = to.slice(0, 10).split('/').reverse().join('-')) : to === '' && (this.dateTo = '');
    // }

    setTableSearch = (tableIndex: number, value: string) => {
        if (tableIndex === 0) {
            this.leftTableSearch = value;
            const filteredSearch = (this.allPaymentsBasket[tableIndex])[this.selectedLeftTableTab].filter((search: any) =>
                search.identity.includes(value) || search.full_name.toLowerCase().includes(value.toLowerCase()) ||
                search.for_month.includes(value) || search.check_date.includes(value) || search.expense_sum.toString().includes(value) ||
                search.payment_method.toLowerCase().includes(value.toLowerCase()) || search.balance_total.toString().includes(value));
            this.setLeftTablePaymentsBasket(filteredSearch);
        }
        else {
            this.rightTableSearch = value;
            const filteredSearch = (this.allPaymentsBasket[tableIndex])[this.selectedRightTableTab].filter((search: any) =>
                search.name.toLowerCase().includes(value.toLowerCase()) || search.expense_sum_total.includes(value) ||
                search.expense_sum.includes(value) || search.balance_total.toString().includes(value));
            this.setRightTablePaymentsBasket(filteredSearch);
        }
    }

    setSelectedTableTab = (tableIndex: number, tab: string) => {
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

    setPaymentsBasketFiltersToSend = (titleName: any, name: any, checked: any, titleIndex: any, filterIndex: any, checkboxIndex: any, fill?: any) => {
        fill === 'checkAll' && (this.paymentsBasketFiltersToSend = { expense_filters: [], student_filters: [] }); //, income_filters: []

        fill === 'unCheckAll' ? this.checkedFilters = this.checkedFilters.map((checkboxes: any) => checkboxes.map((checkbox: any) => checkbox.map(() => false))) :
            fill === 'checkAll' ? this.checkedFilters = this.checkedFilters.map((checkboxes: any) => checkboxes.map((checkbox: any) => checkbox.map(() => true))) :
                (this.checkedFilters[titleIndex][filterIndex][checkboxIndex] = !this.checkedFilters[titleIndex][filterIndex][checkboxIndex]);

        fill === 'unCheckAll' ?
            this.paymentsBasketFilters.map((filters: any) =>
                filters.name !== 'date_filters' && this.paymentsBasketFiltersToSend[filters.name].map((filter: any) =>
                    filter.checked = [])) :
            fill === 'checkAll' ?
                this.paymentsBasketFilters.map((filters: any) =>
                    filters.name !== 'date_filters' &&
                    filters.filters.map((filter: any) =>
                        this.paymentsBasketFiltersToSend[filters.name] = [...this.paymentsBasketFiltersToSend[filters.name], { name: filter.name, checked: filter.checkboxes }])) :
                this.paymentsBasketFiltersToSend[titleName].map((filter: any) =>
                    filter.name === name && (filter.checked.some((exist: any) => exist === checked) ?
                        (filter.checked = filter.checked.filter((value: any) => value !== checked)) :
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

    setPaymentsBasketFilters = (data: any) => {
        this.paymentsBasketFilters = data;

        this.checkedFilters = data.map((filter: any) => filter.name !== 'date_filters' &&
            filter.filters.map((filters: any) => filters.checkboxes && filters.checkboxes.map(() => true))).filter((data: any) => data && data);

        // const date = data.filter(filter => filter.name === 'date_filters')[0]?.filters[0];
        // this.paymentsBasketFiltersDateSelectedOption = [date.display_name, date.name, date.filter_key];
    }

    setRightTablePaymentsBasket = (data: any) => {
        this.rightTableCheckbox = Array(data.length).fill({ checked: false, fk_id: -1 });
        this.rightTableSelectedItems = Array(data.length).fill({ checked: false, fk_id: -1 });
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.rightTablePaymentsBasket = data.concat(moreRows);
    }

    setLeftTablePaymentsBasket = (data: any, dontCheckRightTable?: boolean) => {
        this.leftTableCheckbox = data.map((item: any) => ({ checked: item.is_printable, fk_id: -1 }));
        const moreRows = data.length < 10 ? Array(10 - data.length).fill('') : [];
        this.leftTablePaymentsBasket = data.concat(moreRows);
        !dontCheckRightTable && this.setRightTableSelectedItems();
    }

    setAllPaymentsBasket = (data: any) => {
        data && data.length > 1 && Object.keys(data[1]).map(rightTableTabName =>
            data[1][rightTableTabName].map((rightTableItem: any, index: number) =>
                Object.keys(data[0]).map(leftTableTabName =>
                (data[1][rightTableTabName][index][`${leftTableTabName}_sum`] = data[0][leftTableTabName].filter((leftTableItem: any) =>
                    rightTableItem[`fk_${rightTableTabName}_id`] === leftTableItem[`fk_${rightTableTabName}_id`]
                ).length))
            )
        )

        this.allPaymentsBasket = data;
        data && data.length > 0 && data[0][this.selectedLeftTableTab] && this.setLeftTablePaymentsBasket(data[0][this.selectedLeftTableTab]);
        data && data.length > 1 && data[1][this.selectedRightTableTab] && this.setRightTablePaymentsBasket(data[1][this.selectedRightTableTab])
    }

    fetchFilteredPaymentsBasket = (body: any) => {
        this.setAllPaymentsBasket(null);
        Fetch.Post('payment_basket', {})
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

    fetchEditExpense = async (id: any, body: any) => {
        return await Fetch.Put(`expense/${id}`, body)
            .then(res => res.error)
            .catch(err => console.error(err))
    }

    fetchDeleteExpense = async (id: any, body: any) => {
        return await Fetch.Delete(`expense${id ? `/${id}` : ''}`, body)
            .then(res => res.error)
            .catch(err => console.error(err))
    }

    fetchPrint = async (onlyShown: boolean) => {
        let body: any = [];
        onlyShown && this.allPaymentsBasket[0][this.selectedLeftTableTab].map((item: any) => item.is_printable && (body = [...body, item.expense_id]));

        if (!(onlyShown && body.length === 0)) {
            return await Fetch.Post('expense/print_payment', body, true)
                .catch((err: string) => console.error(err))
        }
    }

    fetchBankAccount = () => {
        Fetch.Get('bank_account?verbose=true')
            .then((res: any) => this.setBankAccount(res))
            .catch((err: string) => console.error(err))
    }

    fetchTrendCoordinator = () => {
        Fetch.Get('trend_coordinator')
            .then(res => this.setTrendCoordinator(res))
            .catch(err => console.error(err))
    }
}

export default new PaymentsBasketStore();