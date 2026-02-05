import { makeAutoObservable } from 'mobx';
// import * as Fetch from '../../Fetch';

class ImportDataStore {
    constructor() {
        makeAutoObservable(this);
    }

}

export default new ImportDataStore();