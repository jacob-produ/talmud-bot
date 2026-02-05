import React, { useEffect, useState } from 'react'
import { SiGooglesheets } from 'react-icons/si';


const GoogleSheetsLink = ({headers,data,store,table}) => {
    const [jsonFile,setJsonFile] = useState()

    const JSONConverted=()=>{
        let exportObj={}
        let newData = []
        for(let i=0;i<data.length;i++){
            let tempObj ={}

            for (const [key, value] of Object.entries(data[i])) {
              tempObj[headers[key]]= value
            }
            newData.push(tempObj)

        }
        exportObj['table']=table
        exportObj['data']=newData

        let convertedData = JSON.stringify(exportObj)
        setJsonFile(convertedData)
        store.fetchGoogleSheets(convertedData)
    }

    
  return (
    <div onClick={JSONConverted} style={{ marginRight:'5px' }}>
    <SiGooglesheets size='1.3em' title='GoogleSheets' style={{ cursor: 'pointer' }} />
    </div>
  )
}

export default GoogleSheetsLink