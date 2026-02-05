import { borderRadius } from "@mui/system";
import React, { useEffect ,useState} from "react";
import TableTemplate from "../UI/TableTemplate";


const CSVFilePopup = (props) => {
  console.log('CSVFilePopup');
  const [headers,setHeaders]=useState([])


  const {data}=props
  console.log(data);
  useEffect(()=>{
    if(data.errors.length>0){
      const tableTitles= Object.keys(data.errors[0])
      setHeaders(tableTitles)

    }

  },[data])
  const convertTableData=()=>{

  }

  return (
    <div style={{direction: 'rtl',padding:'20px', backgroundColor: 'gray' ,borderRadius:'15px'}}>
      <h3  style={{width:'100%', textAlign:'center'}}>{data.title}</h3>
      <div  className="success">
        <label>רשומות שהצליחו:</label>
        <p  style={{marginRight:'30px'}}>{data.success}</p>
      </div>
    
      <div className="table">
        <label>רשומות שנכשלו:</label>
        {headers?<TableTemplate Headers={headers} bodyCellData={data.errors} />:'0'}
      </div>
    </div>
  );
};

export default CSVFilePopup;
