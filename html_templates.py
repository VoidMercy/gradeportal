classtemplate = """<!-- Accordion card -->
    <div class="card">

        <!-- Card header -->
        <div class="card-header" role="tab" id="headingOne">
            <a class="collapsed" data-toggle="collapse" data-parent="#accordionEx" href="#g{id}" aria-expanded="true" aria-controls="g{id}">
                <h5 class="mb-0">
                    {head} <i class="fa fa-angle-down rotate-icon"></i> <span class="pull-right pr-3" id="{classnamegrade}">{grade}</span>
                </h5>
            </a>
        </div>

        <!-- Card body -->
        <div id="g{id}" class="collapse" role="tabpanel" aria-labelledby="headingOne">
            <div class="card-body">
    
<table class="table" id="categories">
  <thead>
    <tr>
      <th scope="col">Category</th>
      <th scope="col">Weight</th>
      <th scope="col">Points/Max Points</th>
      <th scope="col">Grade</th>
    </tr>
  </thead>
  <tbody>
  {cats}
  </tbody>
</table>
            
                <table class="table" id="{classnametable}">
  <thead>
    <tr>
      <th scope="col">Assignment Name</th>
      <th scope="col">Category</th>
      <th scope="col">Due Date</th>
      <th scope="col">Points</th>
      <th scope="col">Possible</th>
    </tr>
  </thead>
  <tbody>
  {rows}
  </tbody>
</table>


<button type="button" class="btn btn-deep-purple pull-right pt" onclick="calc_grade('{classnametable}','{classnamegrade}')">recalculate</button>
            </div>
        </div>
    </div>
    <!-- Accordion card -->"""

classtemplate2 = """<!-- Accordion card -->
    <div class="card">

        <!-- Card header -->
        <div class="card-header" role="tab" id="headingOne">
            <a class="collapsed" data-toggle="collapse" data-parent="#accordionEx" href="#m{id}" aria-expanded="true" aria-controls="m{id}">
                <h5 class="mb-0">
                    {head} <i class="fa fa-angle-down rotate-icon"></i> <span class="pull-right pr-3">{grade}</span>
                </h5>
            </a>
        </div>

        <!-- Card body -->
        <div id="m{id}" class="collapse" role="tabpanel" aria-labelledby="headingOne">
            <div class="card-body">
                <table class="table">
  <thead>
    <tr>
      <th scope="col">Category</th>
      <th scope="col">Due Date</th>
      <th scope="col">Points</th>
      <th scope="col">Possible</th>
    </tr>
  </thead>
  <tbody>
  {rows}
  </tbody>
</table>
            </div>
        </div>
    </div>
    <!-- Accordion card -->"""

classtemplate3 = """<!-- Accordion card -->
    <div class="card">

        <!-- Card header -->
        <div class="card-header" role="tab" id="headingOne">
            <a class="collapsed" data-toggle="collapse" data-parent="#accordionEx" href="#up{id}" aria-expanded="true" aria-controls="up{id}">
                <h5 class="mb-0">
                    {head} <i class="fa fa-angle-down rotate-icon"></i> <span class="pull-right pr-3">{grade}</span>
                </h5>
            </a>
        </div>

        <!-- Card body -->
        <div id="up{id}" class="collapse" role="tabpanel" aria-labelledby="headingOne">
            <div class="card-body">
                <table class="table">
  <thead>
    <tr>
      <th scope="col">Category</th>
      <th scope="col">Due Date</th>
      <th scope="col">Possible</th>
    </tr>
  </thead>
  <tbody>
  {rows}
  </tbody>
</table>
{message}
            </div>
        </div>
    </div>
    <!-- Accordion card -->"""



row = """<tr>
      <th scope="row">{}</th>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
    </tr>"""
row = """<tr>
      <th scope="row">{}</th>
      <td>{}</td>
      <td>{}</td>
      <td><input type="text" id="assignmentname" value="{}"></td>
      <td>{}</td>
    </tr>"""


row2 = """<tr>
      <th scope="row">{}</th>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
    </tr>"""

row3 = """<tr>
      <th scope="row">{}</th>
      <td>{}</td>
      <td>{}</td>
    </tr>"""

buttontemp = """<button type="button" class="btn btn-danger btn-sm pull-right" id="{}" onclick="remove_assignment('{}')">remove</button>"""
buttontemp2 = """<button type="button" class="btn btn-danger btn-sm pull-right" id="{}" onclick="remove_upcoming('{}')">remove</button>"""

categorydroptemp = """<option value="{}">{}</option>"""