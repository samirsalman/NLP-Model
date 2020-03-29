import React from "react";
import Grid from "@material-ui/core/Grid";
import { useTheme } from "@material-ui/core/styles";
import NoItem from "../noitem.png";

export default function LoadingComponent() {
  const theme = useTheme();
  return (
    <Grid
      container
      spacing={0}
      direction="column"
      alignItems="center"
      justify="center"
    >
      <Grid item>
        <img src={NoItem}></img>
      </Grid>
    </Grid>
  );
}
