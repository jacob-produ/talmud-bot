import React from 'react';
import '../../styles/reception/ReceptionPopup';

const ReceptionPopup = (props) => {

    const InputDetail = ({ lableName, inputType = 'text' }) => {
        return <label className='receptionPopup__row__columnDetail__input'>
            {lableName}: <input type={inputType} />
        </label>
    }

    return (
        <div id='popupContainer'>
            <div className='receptionPopup'>
                <div className='receptionPopup__row'>
                    <div className='receptionPopup__row__title'>פרטי בעל החשבון - התורם</div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='שם' />
                        <InputDetail lableName='מזהה' />
                        <InputDetail lableName='טלפון' />
                        <InputDetail lableName='מייל' />
                    </div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='מספר בנק' />
                        <InputDetail lableName='מספר סניף' />
                        <InputDetail lableName='מספר חשבון' />
                    </div>
                </div>
                <div className='receptionPopup__row'>
                    <div className='receptionPopup__row__title'>פרטי ההו"ק</div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='סכום' />
                        <InputDetail lableName='תאריך לחיוב' />
                        <InputDetail lableName='יתרת חיובים' />
                        <InputDetail lableName='הקמה ע"י מוסד/תורם' />
                    </div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='הגבלת סכום' />
                        <InputDetail lableName='הגבלת תאריך לחיוב' />
                        <InputDetail lableName='הגבלת תאריך אחרון' />
                        <InputDetail lableName='שיוך' />
                    </div>
                </div>
                <div className='receptionPopup__row'>
                    <div className='receptionPopup__row__title'>סטטוס ההו"ק</div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='סטטוס משני' />
                        <InputDetail lableName='תאריך שליחת טופס' />
                        <InputDetail lableName='תאריך קבלת הודעת הודעת הרשאה' />
                        <InputDetail lableName='תאריך הודעת ביטול הרשאה' />
                    </div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='תאריך תחילת השהייה' />
                        <InputDetail lableName='תאריך סיום השהייה' />
                        <InputDetail lableName='תאריך יצירה במערכת' />
                    </div>
                </div>
                <div className='receptionPopup__row'>
                    <div className='receptionPopup__row__title'>היסטוריה</div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='תאריך' />
                    </div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='סכום' />
                    </div>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='סטטוס' />
                    </div>
                </div>
                <div className='receptionPopup__row'>
                    <div className='receptionPopup__row__columnDetail'>
                        <InputDetail lableName='סה"כ הצלחות' />
                        <InputDetail lableName='סה"כ נגבה' />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ReceptionPopup;