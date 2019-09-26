from mesa.visualization.modules import TextElement

"""
     Contains the legend of the model. The css attributes cannot be moved to a separate css stylesheet 
     because the mesa stylesheet overwrites it.
    """


class ModelLegend(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        legend = '''
         <fieldset>
          <legend style="font-size:16px; margin-top:20px;">Model Legend:</legend>
          <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:blue'></div> <p style="font-size:16px; margin-bottom: 15px"> Male Civilian Agent </p> </div>
          <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:purple'></div> <p style="font-size:16px; margin-bottom: 15px"> Female Civilian Agent </p> </div>
           <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:red'></div> <p style="font-size:16px; margin-bottom: 15px"> Fire </p> </div>
           <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:green'></div> <p style="font-size:16px; margin-bottom: 15px"> Emergency exit </p> </div>
            <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:black'></div><p style="font-size:16px; margin-bottom: 15px"> Wall </p> </div>
           </fieldset>
         '''

        return legend
