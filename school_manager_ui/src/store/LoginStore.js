import { makeAutoObservable } from 'mobx';
import * as Fetch from '../fetches/Fetch';

class LoginStore {
    constructor() {
        makeAutoObservable(this);
    }

    userName = '';
    password = '';
    rememberMe = false;
    errorMessage = '';
    loader = false;

    setLoader = (load) => {
        this.loader = load;
    }

    changeUserName = (value) => {
        this.userName = value;
        this.setErrorMessage('');
    }

    changePassword = (value) => {
        this.password = value;
        this.setErrorMessage('');
    }

    changeRememberMe = (checked) => {
        this.rememberMe = checked;
        this.setErrorMessage('');
    }

    setErrorMessage = (err) => {
        !(this.errorMessage === '' && err === '') && (this.errorMessage = err);
    }

    login = async () => {
        this.setErrorMessage('');
        this.loader = true;
        if (this.userName.trim() !== '' && this.password.trim() !== '') {
            return await Fetch.Post('auth/login', { username: this.userName, password: this.password, remember_me: this.rememberMe })
                .then(res => {
                    res.error && this.setErrorMessage(res.message);
                    return res.error;
                })
                .catch(err => { console.error(err); this.setErrorMessage('יש בעיה, נסה מאוחר יותר'); })
        }
        else {
            this.setErrorMessage('מלא את השדות שם משתמש וסיסמה');
            return true;
        };
    }
}

export default new LoginStore();