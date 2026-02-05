import React from 'react';
import PropTypes from 'prop-types';

const FinanceReportFilters = (props) => {
    return (
        <div className='disableTextSelectionHighlighting financeReportFiltersContainer' >
            {props.data.map((filters, titleIndex) => <React.Fragment key={filters.title}>
                <div className='financeReportFiltersPosition' >
                    <div className='financeReportFiltersTitle' >{filters.title}</div>
                    {
                        filters.title === 'תאריכים' ?
                            <div style={{ display: 'flex', height: '70%' }}>
                                <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-evenly', alignItems: 'center' }}>
                                    <select style={{ width: 'fit-content', fontSize: '1em' }} onChange={(e) => props.dateSelectOption(e.target.value)}>
                                        {filters.filters.map((option, optionIndex) =>
                                            <option key={optionIndex} value={[option.display_name, option.name, option.filter_key]}>{option.display_name}</option>)}
                                    </select>
                                    <input type='date' style={{ fontSize: '1em' }} value={props.dateFrom} onChange={e => props.onDateFrom(e.target.value)} />
                                    <input type='date' style={{ fontSize: '1em' }} value={props.dateTo} onChange={e => props.onDateTo(e.target.value)} />
                                    <div style={{ color: 'blue', textDecoration: 'underline', cursor: 'pointer' }} onClick={() => props.cleanDate()}>נקה</div>
                                </div>
                            </div> :
                            <div style={{ display: 'flex' }}>
                                {filters.filters.map((filter, filterIndex) => <div key={filterIndex} className='checksDataContainer' style={{ position: 'relative', display: 'flex', flexDirection: 'column', marginRight: filterIndex > 0 && '1.5em' }}>
                                    <div style={{ fontWeight: '500', textDecoration: 'underline' }}>{filter.display_name}</div>
                                    {filter.checkboxes.map((value, checkboxIndex) => <div key={checkboxIndex}>
                                        <label style={{ cursor: 'pointer' }}>
                                            <input className='checkboxFinanceReportFilter' type='checkbox' title_index={titleIndex} filter_index={filterIndex}
                                                checkbox_index={checkboxIndex} onChange={e => props.onChange(filters.name, filter.name, value, titleIndex, filterIndex, checkboxIndex)} />
                                            {value}
                                        </label>
                                    </div>)}
                                </div>)}
                            </div>}
                </div>
                <hr style={{ margin: 'auto 1em', border: 'none', borderLeft: '1px dashed rgba(158 158 158 / 0.8)', height: '50%', width: '1px' }} />
            </React.Fragment>)}
        </div>
    )
}

FinanceReportFilters.propTypes = {
    data: PropTypes.arrayOf(PropTypes.object),
    onChange: PropTypes.func.isRequired,
    dateSelectOption: PropTypes.func,
    dateFrom: PropTypes.string,
    dateTo: PropTypes.string,
    onDateFrom: PropTypes.func,
    onDateTo: PropTypes.func,
    cleanDate: PropTypes.func,
}

export default FinanceReportFilters;