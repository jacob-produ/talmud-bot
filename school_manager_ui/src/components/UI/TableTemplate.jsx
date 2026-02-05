import * as React from "react";
import { styled } from "@mui/material/styles";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import {Paper} from "@mui/material";

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    backgroundColor: theme.palette.common.black,
    color: theme.palette.common.white,
  },
  [`&.${tableCellClasses.body}`]: {
    fontSize: 14,
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  "&:nth-of-type(odd)": {
    backgroundColor: theme.palette.action.hover,
  },
  // hide last border
  "&:last-child td, &:last-child th": {
    border: 0,
  },
}));

const TableTemplate = (props) => {
  return (
    <TableContainer component={Paper}>
      <Table sx={{marginRight:'30px' , minWidth: 700 }} aria-label="customized table">
        <TableHead>
          <TableRow>
            {props.Headers.map((field) => (
              <StyledTableCell align="right">{field}</StyledTableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {props.bodyCellData.map((rows) => {
            const cellData = Object.values(rows);
            return (
              <StyledTableRow key={rows.error}>
                {cellData.map((cell) => (
                  <StyledTableCell align="right">{cell}</StyledTableCell>
                ))}
              </StyledTableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default TableTemplate;
