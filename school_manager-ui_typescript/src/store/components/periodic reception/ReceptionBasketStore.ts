import { makeAutoObservable } from 'mobx';
// import * as Fetch from '../../Fetch';

class ReceptionBasketStore {
    constructor() {
        makeAutoObservable(this);
    }

}

export default new ReceptionBasketStore();