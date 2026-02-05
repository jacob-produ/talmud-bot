import React, { useEffect, useState  } from 'react';
import { inject, observer } from 'mobx-react';
import Container from '../containers/Container';
import * as Fetch from '../../fetches/Fetch';
import '../../styles/payment report/PaymentReport.css';

const formIds =[
    {
        display_name: 'אישור רווחה',
        id: 'social-services-form'
    },
    {
        display_name: 'אישור לימודים',
        id: 'student-approval-form'
    },
    {
        display_name: 'איושר לימודים עם מסלול',
        id: 'student-approval-form-with-course'
    },
    {
        display_name: 'אישור ארנונה',
        id: 'property-tax-form'
    }
]

const SelectData = ({ titles, children }) => {
    return <div style={{ display: 'flex', marginBottom: '5px' }}>
        <div style={{ marginLeft: '5px' }}>
            {titles.map((title, index) => <div key={index} style={{ marginTop: index > 0 && '5px' }}>{title}:</div>)}
        </div>
        {children}
    </div>
}

const StudentForm = (props) => {
    const [formId, setFormId] = useState(0);
    const [formAttributes, setFormAttributes] = useState({});
    const [inputData, setInputData] = useState({});
    const [formComp, setFormComp] = useState(null);
    const [formAttributesArr, setFormAttributesArr] = useState([]);
    const [studentCourseRegistrationId, setStudentCourseRegistrationId] = useState(1);


    useEffect(() => {

    }, [])

    const HandleFormChoosing = (formId) => {
        console.log(formId);
        setFormId(formId)

        // Fetch.Get(`form_attributes?form_id=${formId}`)
        Fetch.Get(`form_attributes?form_id=${formId}`)
            .then(res => {
                setFormAttributes(res);
                console.log("got: " + JSON.stringify(res))
                BuildFormComp();
                })
            .catch(err => console.error(err))
    }

    const HandleSubmit = (event) => {
        event.preventDefault()
        const body = {'args_dict': inputData}
        Fetch.Post(`generate_pdf?form_id=${formId}&student_course_registration_id=${studentCourseRegistrationId}`, inputData, true)
            .then((response) => response.blob())
            .then((blob) => {
                // Create blob link to download
                const url = window.URL.createObjectURL(
                    new Blob([blob]),
                );
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute(
                    'download',
                    `${formId}.pdf`,
                );

                // Append to html link element page
                document.body.appendChild(link);

                // Start download
                link.click();

                // Clean up and remove the link
                link.parentNode.removeChild(link);
            })
            .catch(err => console.error(err))
    }

    const HandleInputData = (key, value) => {
        let currInputData = inputData;
        currInputData[key] = value;
        setInputData(currInputData);
    }

    const BuildFormComp = () => {
        // if(formAttributes) {
            let formAttr = []
            Object.keys(formAttributes).map(key => {formAttr.push(formAttributes[key].display_name)})
            setFormAttributesArr(formAttr)

            const comp = Object.keys(formAttributes).map(key => {
                console.log(key);
                if(formAttributes[key].type !== 'radio') {
                    return (
                        <div>
                            <label style={{cursor: 'pointer'}} key={key}>
                                <input className={key}
                                       type={formAttributes[key].type}
                                       onChange={e => HandleInputData(key, e.target.value)}
                                       style={{
                                           marginTop: '5px',
                                           width: 'fit-content',
                                           height: '1em',
                                           fontSize: '1em',
                                           outline: 'none'
                                       }}/>
                            </label>
                            <br/>
                        </div>
                    )
                } else {
                    const choices = formAttributes[key].values;
                    const radioComp = choices.map(choice => {
                        return (
                            <div>
                                <input className={choice}
                                       name={formAttributes[key]}
                                       type='radio'
                                       onChange={e => HandleInputData(key, e.target.value)}
                                       />
                                <label style={{cursor: 'pointer'}} key={choice}>
                                    {choice}
                                </label>
                            </div>
                        )
                    })
                return radioComp;
                }
            })
            setFormComp(comp);
        // }
    }

    return (
        <Container title='הפקת טופס' childrenStyle={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '15px' }} >
                <div style={{ marginLeft: '10px', whiteSpace: 'nowrap' }}>בחר טופס:</div>
                <select style={{ width: 'fit-content', fontSize: '1em' }} onChange={(e) => HandleFormChoosing(e.target.value)}>
                    {formIds.map((option, optionIndex) =>
                        <option key={optionIndex} value={option.id}>{option.display_name}</option>)}
                </select>
            </div>

            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '15px' }} >
                <div className='paymentReportFiltersContainer' style={{ flexDirection: 'column', justifyContent: 'flex-start' }}>
                    <SelectData titles={formAttributesArr} >
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <form>
                                {formComp}
                                {formComp &&
                                    <div>
                                        <button type="submit" onClick={HandleSubmit}>הפק דוח</button>
                                    </div>
                                }
                            </form>
                        </div>
                    </SelectData>
                </div>
            </div>


        </Container>
    )
}

export default inject('rootStore')(observer(StudentForm));