import { makeAutoObservable } from 'mobx';
import * as Fetch from '../../Fetch';

class LoginStore {
    constructor() {
        makeAutoObservable(this);
    }

    userName: string = '';
    password: string = '';
    rememberMe: boolean = false;
    errorMessage: string = '';
    loader: boolean = false;

    setLoader = (load: boolean) => {
        this.loader = load;
    }

    changeUserName = (user_name: string) => {
        this.userName = user_name;
        this.setErrorMessage('');
    }

    changePassword = (password: string) => {
        this.password = password;
        this.setErrorMessage('');
    }

    changeRememberMe = (remember: boolean) => {
        this.rememberMe = remember;
        this.setErrorMessage('');
    }

    setErrorMessage = (error_message: string) => {
        this.errorMessage !== '' && error_message !== '' && (this.errorMessage = error_message);
    }

    fetchLogin = async () => {
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