import { makeAutoObservable } from 'mobx';
// import * as Fetch from '../../Fetch';

class BankAccountStore {
    constructor() {
        makeAutoObservable(this);
    }

}

export default new BankAccountStore();