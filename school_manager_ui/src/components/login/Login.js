import React from 'react';
import { inject, observer } from 'mobx-react';
import { useHistory } from 'react-router-dom';
import { Spin } from "react-loading-io";
import '../../styles/login/Login.css';

const Login = (props) => {
    const history = useHistory();

    const { loginStore } = props.rootStore;

    const HandleSubmit = (event) => {
        event.preventDefault();
        loginStore.login()
            .then(res => {
                loginStore.setLoader(false);
                if (!res && res !== undefined) {
                    localStorage.setItem('remember', loginStore.rememberMe);
                    localStorage.setItem('userName', loginStore.userName);
                    sessionStorage.setItem('login', 'true');
                    sessionStorage.setItem('route', '/finance-report');
                    loginStore.setErrorMessage('');
                    history.push('/finance-report');
                }
            });
    }

    return (
        <div className='loginPage' >
            <div className='loginBorder'> {/** gradientBorderBox */}
                <div className='loginBorderPosition' >
                    {/* <img className='loginLogo' alt='Blyzer' src={require('../../assets/images/LOGO.png')} /> */}
                    <div className='loginTitle' >כניסה</div>
                    <form className='loginForm' onSubmit={HandleSubmit}>
                        <input className='loginInput' type='text' placeholder='שם משתמש' onChange={(e) => loginStore.changeUserName(e.target.value)} />
                        <input className='loginInput' type='password' placeholder='סיסמה' onChange={(e) => loginStore.changePassword(e.target.value)} />
                        <div className='loginErrorMessage'>
                            {loginStore.errorMessage.includes('Incorrect') ? 'שם משתמש או סיסמה שגויים' : loginStore.errorMessage}
                        </div>
                        {loginStore.loader && <div style={{ display: 'flex', justifyContent: 'center', marginTop: '-2em', marginBottom: '2em' }}><Spin size={50} color='rgba(0 0 0 / 0.7)' /></div>}
                        <button className='loginSubmit disableTextSelectionHighlighting' >התחבר</button>
                        <label className='loginInputCheckbox disableTextSelectionHighlighting' >
                            <input type='checkbox' placeholder='remember' checked={loginStore.rememberMe} onChange={e => loginStore.changeRememberMe(e.target.checked)} />
                            זכור אותי
                        </label>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default inject('rootStore')(observer(Login));