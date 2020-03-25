import React, { useState } from "react";
import {
  Grid,
  Paper,
  List,
  Tabs,
  Tab,
  ListItem,
  ListItemText,
  ListSubheader
} from "@material-ui/core";
import ChartComponent from "./ChartComponent";

export default function ResultsComponent(props) {
  const [selected, setSelected] = useState(0);

  const changeTab = (event, value) => {
    setSelected(value);
  };

  return (
    <Grid item style={{ width: "90%" }}>
      <Paper style={{ padding: "24px" }}>
        <Grid container direction="row" justify="space-between">
          <Grid item>
            {props.columnText}
            <ChartComponent col={props.columnIndex}></ChartComponent>
          </Grid>
          <Grid item>
            <Grid container direction="column">
              <Paper square>
                <Tabs
                  value={selected}
                  indicatorColor="primary"
                  textColor="primary"
                  onChange={changeTab}
                  aria-label="disabled tabs example"
                >
                  <Tab
                    label="C1"
                    style={{ backgroundColor: "#1e2a78", color: "white" }}
                  />
                  <Tab
                    label="C2"
                    style={{ backgroundColor: "#f9ff21", color: "black" }}
                  />
                  <Tab
                    label="C3"
                    style={{ backgroundColor: "#ff1f5a", color: "white" }}
                  />
                </Tabs>
              </Paper>
              <List
                style={{
                  width: "100%",
                  maxWidth: 476,
                  position: "relative",
                  overflow: "auto",
                  maxHeight: 600
                }}
              >
                {props.data.elements.map(el => {
                  if (el.cluster === selected) {
                    return (
                      <ListItem>
                        <ListItemText
                          primary={el.phrase}
                          secondary={el.person_id}
                        />
                      </ListItem>
                    );
                  } else {
                    return <div></div>;
                  }
                })}
              </List>
            </Grid>
          </Grid>
        </Grid>
      </Paper>
    </Grid>
  );
}
