import React from "react";
import {
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListSubheader
} from "@material-ui/core";
import ChartComponent from "./ChartComponent";

export default function ResultsComponent(props) {
  return (
    <Grid item style={{ width: "90%" }}>
      <Paper style={{ padding: "24px" }}>
        <Grid container direction="row" justify="space-between">
          <Grid item>
            {props.columnText}
            <ChartComponent col={props.columnIndex}></ChartComponent>
          </Grid>
          <Grid item>
            <List
              style={{
                width: "100%",
                maxWidth: 360,
                position: "relative",
                overflow: "auto",
                maxHeight: 300
              }}
            >
              {props.data.cendroids.map(centroid => (
                <li key={`centroid-${centroid}`}>
                  <ul>
                    <ListSubheader
                      style={{
                        backgroundColor:
                          centroid.cluster === 0
                            ? "#c43a31"
                            : centroid.cluster === 1
                            ? "#ff5875"
                            : "#000",
                        color: "#fff",
                        fontWeight: 800
                      }}
                    >
                      {centroid.phrase.toUpperCase()}
                    </ListSubheader>
                    {props.data.elements.map(el => {
                      if (el.cluster === centroid.cluster) {
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
                  </ul>
                </li>
              ))}
            </List>
          </Grid>
        </Grid>
      </Paper>
    </Grid>
  );
}
