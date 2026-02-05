import { makeAutoObservable } from 'mobx';
// import * as Fetch from '../../Fetch';

class TransactionsReportStore {
    constructor() {
        makeAutoObservable(this);
    }

}

export default new TransactionsReportStore();