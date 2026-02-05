import React from "react";
import Store from '../../store/RootStore';

import Modal from "../UI/Modal";
import CSVFilePopup from "./CSVFilePopup";
import { Spin } from "react-loading-io";

const Popup = (props) => {
  const { uploadCSVFile } = Store;
  return (
    <Modal onClose={props.onClose}>
      {uploadCSVFile.loader ? <div style={{ display: 'flex', justifyContent: 'center', alignContent:'center' }}>
        <Spin size={150} color='rgba(0 0 0 / 0.7)' />
      </div>:<div style={{ width:'100%', height:'90%', overflowY:'scroll',display: 'flex', gap: '25PX', alignContent:'center', flexDirection:'column' }}>
      <div style={{ width:'20px' }}>
      <button onClick={props.onClose}>Close</button>

      </div>
      {props.data.map((info) => {
        if(!info.popup_results){
          return props.downloadJson(true)
        }
        props.downloadJson(false)
        return info.popup_results.map((index)=><CSVFilePopup key={index.name} data={index} />) 
      }
      )}</div>}
    </Modal>
  );
};

export default Popup;
