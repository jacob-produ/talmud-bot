import React from 'react';

type filters = {
    checkboxes?: string[],
    filter_key?: string,
    display_name: string,
    name: string
}

export type filter_data = {
    filters: filters[],
    name: string,
    title: string
}

interface Props {
    data: filter_data[],
    onChange: (filter_name: string, name: string, value: string, titleIndex: number, filterIndex: number, checkboxIndex: number) => void,
    dateSelectOption?: (date: string) => void,
    dateFrom?: string,
    dateTo?: string,
    onDateFrom?: (date: string) => void,
    onDateTo?: (date: string) => void,
    cleanDate?: () => void,
}

const Filters: React.FC<Props> = (props) => {
    return (
        <div className='filters' >
            {props.data.map((filters, titleIndex) => <React.Fragment key={filters.title}>
                <div className='filters__filter' >
                    <div className='filters__filter__title' >{filters.title}</div>
                    {
                        filters.title === 'תאריכים' ?
                            <div className='filters__filter__date' >
                                <select style={{ width: 'fit-content', fontSize: '1em' }} onChange={(e) => props.dateSelectOption && props.dateSelectOption(e.target.value)}>
                                    {filters.filters.map((option, optionIndex) =>
                                        <option key={optionIndex} value={option.filter_key ? [option.display_name, option.name, option.filter_key] :
                                            [option.display_name, option.name]}>{option.display_name}</option>)}
                                </select>
                                <input type='date' style={{ fontSize: '1em' }} value={props.dateFrom} onChange={e => props.onDateFrom && props.onDateFrom(e.target.value)} />
                                <input type='date' style={{ fontSize: '1em' }} value={props.dateTo} onChange={e => props.onDateTo && props.onDateTo(e.target.value)} />
                                <div style={{ color: 'blue', textDecoration: 'underline', cursor: 'pointer' }} onClick={props.cleanDate}>נקה</div>
                            </div> :
                            <div style={{ display: 'flex' }}>
                                {filters.filters.map((filter, filterIndex) => <div key={filterIndex} className='checksDataContainer' style={{ position: 'relative', display: 'flex', flexDirection: 'column', marginRight: filterIndex > 0 ? '1.5em' : 'auto' }}>
                                    <div style={{ fontWeight: '500', textDecoration: 'underline' }}>{filter.display_name}</div>
                                    {filter.checkboxes?.map((value, checkboxIndex) => <div key={checkboxIndex}>
                                        <label style={{ cursor: 'pointer' }}>
                                            {/* title_index={titleIndex} filter_index={filterIndex} checkbox_index={checkboxIndex} */}
                                            <input className='checkboxFinanceReportFilter' type='checkbox' onChange={e => props.onChange(filters.name, filter.name, value, titleIndex, filterIndex, checkboxIndex)} />
                                            {value}
                                        </label>
                                    </div>)}
                                </div>)}
                            </div>}
                </div>
                <hr style={{ margin: 'auto 1em', border: 'none', borderLeft: '1px dashed rgba(158 158 158 / 0.8)', height: '50%', width: '1px' }} />
            </React.Fragment>)}
        </div>
    );
}

export default Filters;