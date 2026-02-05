import React, { useEffect } from 'react';
import Store from '../../store';
import { observer } from 'mobx-react';
import { useNavigate } from 'react-router-dom';
import { ClipLoader } from "react-spinners";

const Login = () => {
    const navigate = useNavigate();
    const { loginStore } = Store;

    useEffect(() => {
        sessionStorage.getItem('login') && navigate(`${sessionStorage.getItem('route') || '/login'}`);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const HandleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        loginStore.fetchLogin()
            .then(res => {
                loginStore.setLoader(false);
                if (!res && res !== undefined) {
                    localStorage.setItem('remember', loginStore.rememberMe.toString());
                    localStorage.setItem('userName', loginStore.userName);
                    sessionStorage.setItem('login', 'true');
                    sessionStorage.setItem('route', '/finance-report');
                    loginStore.setErrorMessage('');
                    navigate('/finance-report');
                }
            });
    }

    return (
        <div className='login' >
            <div className='login__border'>
                <div className='login__border__position' >
                    {/* <img className='loginLogo' alt='Scholl Manager' src={require('../../assets/images/LOGO.png')} /> */}
                    <div className='login__title' >כניסה</div>
                    <form className='login__form' onSubmit={HandleSubmit}>
                        <input className='login__form__input' type='text' placeholder='שם משתמש' onChange={(e) => loginStore.changeUserName(e.target.value)} />
                        <input className='login__form__input' type='password' placeholder='סיסמה' onChange={(e) => loginStore.changePassword(e.target.value)} />
                        <button className='login__form__submit' >התחבר</button>
                        <label className='login__form__input__checkbox' >
                            <input type='checkbox' placeholder='remember' checked={loginStore.rememberMe} onChange={e => loginStore.changeRememberMe(e.target.checked)} />
                            זכור אותי
                        </label>
                    </form>
                    <div className='login__error_message'>{loginStore.errorMessage.includes('Incorrect') ? 'שם משתמש או סיסמה שגויים' : loginStore.errorMessage}</div>
                    <ClipLoader loading={loginStore.loader} size='2.5em' color='rgba(0 0 0 / 0.7)' />
                </div>
            </div>
        </div>
    )
}

export default observer(Login);