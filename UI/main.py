from flask import Flask, request, render_template, redirect, url_for
import subprocess
import json
import hashlib

app = Flask(__name__)

def terraform_execute(region_option, destroy):
    subprocess.run(f'''cd ../terraform/{region_option}
        terraform validate
        terraform plan{destroy} -out="tfplan.out" -var-file="terraform.tfvars.json"
        terraform apply "tfplan.out"
        terraform output -json > out.json
        rm tfplan.out
    ''', shell=True)


@app.route('/', methods = ["GET", "POST"])
def index():
    if request.method == 'POST':
        if request.form.get('region') == 'us-east-1':
            region_option = "us-east-1"
        elif request.form.get('region') == 'us-east-2':
            region_option = "us-east-2"
        else:
            return render_template('index.html', form=request.form)
        subprocess.run(f'cd ../terraform/{region_option}; terraform init', shell=True)
        return redirect(url_for('.region', region_option=region_option))
    return render_template('index.html', form=request.form)

@app.route('/user', methods = ["GET", "POST"])
def user():
    region_option = request.args['region_option']
    try:
        f = open(f"../terraform/{region_option}/out.json", "r")
        data = json.load(f)
        f.close()
        users = [user["name"] for user in data["users"]["value"]]
    except:
        users = []
    if request.method == 'POST':
        if request.form.get('action') == 'Home':
            return redirect(url_for('.region', region_option=region_option))
        with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
            data = json.load(f)
        if request.form['action'] == 'Add user':
            data["users"].append({
                "name": request.form.get('username'),
                "statements": [{
                    "Action": request.form.get('useraction').split(","),
                    "Effect": request.form.get('usereffect'),
                    "Resource": "*"
                }]
            })
        else:
            for user in data["users"]:
                if user["name"] == request.form.get('userremove'):
                    data["users"].remove(user)
                    break
        with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
            json.dump(data, f, indent=4)
        terraform_execute(region_option, "")
    return render_template('user.html', form=request.form, region=region_option, users=users)

@app.route('/region', methods = ["GET", "POST"])
def region():
    region_option = request.args['region_option']
    if request.method == 'POST':
        if request.form.get('user') == 'Create/Delete user':
            return redirect(url_for('.user', region_option=region_option))
        elif request.form.get('action') == 'Back':
            return redirect(url_for('.index'))
        elif request.form.get('action') == 'Create/Configure/Delete VPC':
            return redirect(url_for('.vpc', region_option=region_option))
        elif request.form.get('action') == 'Create/Delete Subnet':
            return redirect(url_for('.subnet', region_option=region_option))
        elif request.form.get('action') == 'Create/Delete Instance':
            return redirect(url_for('.instance', region_option=region_option))
    print(region_option)
    return render_template('region.html', form=request.form, region=region_option)

@app.route('/vpc', methods = ["GET", "POST"])
def vpc():
    region_option = request.args['region_option']
    if request.method == 'GET':
        try:
            f = open(f"../terraform/{region_option}/out.json", "r")
            data = json.load(f)
            f.close()
            vpc_active = False
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
                vpc_active = json.load(f)["vpc"]["active"]
            vpc_name = data["vpc"]["value"]["tags"]["Name"]
            instances = len(data["instances"]["value"])
            subnets = len(data["subnets"]["value"])
            empty = ""
            if vpc_active:
                if instances > 0 or subnets > 0:
                    empty = f"Your VPC with name '{vpc_name}' still has {subnets} subnets and {instances} instances. If you delete the VPC, all of these resources will also be deleted."
                return render_template('vpcConfig.html', form=request.form, region=region_option, name=vpc_name, empty=empty)
            return render_template('vpcCreate.html', form=request.form, region=region_option)
        except:
            f = open(f"../terraform/{region_option}/terraform.tfvars.json", "w")
            json.dump(
                {
                    "vpc":{"cidr_block":"", "tags":{"Name":""}},
                    "subnets":[],
                    "instances":[],
                    "network_interfaces":[],
                    "security_groups":[],
                    "users":[]
                }, f, indent=4
            )
            f.close()
            return render_template('vpcCreate.html', form=request.form, region=region_option)

    elif request.method == 'POST':
        if request.form.get('action') == 'Home':
            return redirect(url_for('.region', region_option=region_option))
        elif request.form.get('action') == 'Create/Delete Security Group':
            return redirect(url_for('.security_group', region_option=region_option))
        destroy = ""
        with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
            data = json.load(f)
        if request.form.get('action') == 'Create VPC':
            data["vpc"]["cidr_block"] = request.form.get('cidr_block')
            data["vpc"]["tags"]["Name"] = request.form.get('vpc_name')
            data["vpc"]["active"] = True
        else:
            data["vpc"]["active"] = False
            destroy = ' -destroy -target="aws_vpc.vpc"'
        with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
            json.dump(data, f, indent=4)
        terraform_execute(region_option, destroy)
        return redirect(url_for('.region', region_option=region_option))

@app.route('/subnet', methods = ["GET", "POST"])
def subnet():
    region_option = request.args['region_option']
    try:
        f = open(f"../terraform/{region_option}/out.json", "r")
        data = json.load(f)
        f.close()
        cidr_block = data["vpc"]["value"]["cidr_block"]
        subnets = list(data["subnets"]["value"].keys())
    except:
        subnets = []
    if request.method == 'POST':
        if request.form.get('action') == 'Home':
            return redirect(url_for('.region', region_option=region_option))
        elif request.form.get('action') == 'Create Subnet':
            subnet_name = request.form.get('subnet_name')
            subnet_cidr = request.form.get('cidr_block')
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
                data = json.load(f)
            data["subnets"].append({
                "cidr_block":subnet_cidr,
                "tags":{"Name":subnet_name},
            })
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
                json.dump(data, f, indent=4)
        elif request.form.get('action') == 'Delete Subnet':
            subnet_name = request.form.get('subnet')
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
                data = json.load(f)
            for subnet in data["subnets"]:
                if subnet["tags"]["Name"] == subnet_name:
                    for nic in data["network_interfaces"]:
                        if nic["subnet"] == subnet["tags"]["Name"]:
                            for inst in data["instances"]:
                                if inst["nic"] == nic["tags"]["Name"]:
                                    data["instances"].remove(inst)
                                    break
                            data["network_interfaces"].remove(nic)
                    data["subnets"].remove(subnet)
                    break
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
                json.dump(data, f, indent=4)
        terraform_execute(region_option, "")
    return render_template('subnet.html', form=request.form, region=region_option, cidr_block=cidr_block, subnets=subnets)

@app.route('/security_group', methods = ["GET", "POST"])
def security_group():
    region_option = request.args['region_option']
    try:
        with open(f"../terraform/{region_option}/out.json", "r") as f:
            data = json.load(f)
        sgs = list(data["security_groups"]["value"].keys())
    except:
        sgs = []
    if request.method == 'POST':
        if request.form.get('action') == 'Home':
            return redirect(url_for('.region', region_option=region_option))
        elif request.form.get('action') == 'Add rules to Security Group':
            if request.form.get('sg_description') == "":
                return render_template('security_group.html', form=request.form, region=region_option, sgs=sgs)
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
                data = json.load(f)
            data["security_groups"].append({
                "name":request.form.get('sg_name'),
                "description":request.form.get('sg_description'),
                "ports":[]
            })
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
                json.dump(data, f, indent=4)
            return redirect(url_for('.rules', region_option=region_option, sg=request.form.get('sg_name')))
        elif request.form.get('action') == 'Delete Security Group':
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
                data = json.load(f)
            for i in range(len(data["security_groups"])):
                if data["security_groups"][i]["name"] == request.form.get('security_group'):
                    data["security_groups"].pop(i)
                    break
            for nic in data["network_interfaces"]:
                if request.form.get('security_group') in nic["security_groups"]:
                    for inst in data["instances"]:
                        if nic["tags"]["Name"] == inst["nic"]:
                            data["instances"].remove(inst)
                            break
                    data["network_interfaces"].remove(nic)
                    break
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
                json.dump(data, f, indent=4)
            terraform_execute(region_option, "")
    return render_template('security_group.html', form=request.form, region=region_option, sgs=sgs)

@app.route('/rules', methods = ["GET", "POST"])
def rules():
    sg = request.args['sg']
    region_option = request.args['region_option']
    if request.method == 'POST':
        if request.form.get('action') == 'Home':
            return redirect(url_for('.region', region_option=region_option))
        elif request.form.get('action') == 'Add rule':
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
                data = json.load(f)
            for i in range(len(data["security_groups"])):
                if data["security_groups"][i]["name"] == sg:
                    data["security_groups"][i]["ports"].append({
                        "from":request.form.get('from'),
                        "to":request.form.get('to'),
                    })
                    break
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
                json.dump(data, f, indent=4)
            return render_template('rules.html', form=request.form, region=region_option, sg=sg)
        elif request.form.get('action') == 'Create Security Group':
            terraform_execute(region_option, "")
            return redirect(url_for('.security_group', region_option=region_option))
    return render_template('rules.html', form=request.form, region=region_option, sg=sg)

@app.route('/instance', methods = ["GET", "POST"])
def instance():
    region_option = request.args['region_option']
    extra = []
    message = ""
    try:
        with open(f"../terraform/{region_option}/out.json", "r") as f:
            data = json.load(f)
        subnets = {sn:data["subnets"]["value"][sn]["cidr_block"] for sn in list(data["subnets"]["value"].keys())}
        sgs = list(data["security_groups"]["value"].keys())
        instances = list(data["instances"]["value"].keys())
    except:
        subnets = {}
        sgs = []
    if request.method == 'POST':
        if request.form.get('action') == 'Home':
            return redirect(url_for('.region', region_option=region_option))
        elif request.form.get('action') == 'Create Instance':
            ok = True
            instance_name = request.form.get('instance_name')
            instance_type = request.form.get('type')
            instance_subnet = request.form.get('subnet')
            instance_ips = request.form.get('instance_ip').split(",")
            instance_sgs = []
            sg_sel = False
            for sg in sgs:
                mark = request.form.get(sg)
                if mark == "on":
                    sg_sel = True
                    instance_sgs.append(sg)
            if instance_name == '':
                ok = False
                extra.append("Missing Instance Name!")
            if instance_type == '':
                ok = False
                extra.append("Missing Instance Type!")
            if instance_subnet == '':
                ok = False
                extra.append("Missing Instance Subnet!")
            if instance_ips[0] == '':
                ok = False
                extra.append("Missing Instance IP address!")
            if not sg_sel:
                ok = False
                extra.append("Missing Instance Secutiry Group selection!")
            if ok:
                nic_name = hashlib.md5(instance_name.encode()).hexdigest()
                with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
                    data = json.load(f)
                data["instances"].append({
                    "instance_type" : instance_type,
                    "nic" : nic_name,
                    "tags" : {"Name" : instance_name}
                })
                data["network_interfaces"].append({
                    "subnet" : instance_subnet,
                    "private_ips" : instance_ips,
                    "security_groups" : instance_sgs,
                    "tags" : {"Name" : nic_name}
                })
                with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
                    json.dump(data, f, indent=4)
                terraform_execute(region_option, "")
                message = "Instance created with success!"
        if request.form.get('action') == 'Delete Instance':
            instance_name = request.form.get('instance')
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "r") as f:
                data = json.load(f)
            for inst in data["instances"]:
                if inst["tags"]["Name"] == instance_name:
                    for nic in data["network_interfaces"]:
                        if nic["tags"]["Name"] == inst["nic"]:
                            data["network_interfaces"].remove(nic)
                            break
                    data["instances"].remove(inst)
                    break
            with open(f"../terraform/{region_option}/terraform.tfvars.json", "w") as f:
                json.dump(data, f, indent=4)
            terraform_execute(region_option, "")
            message = "Instance deleted with success!"
    return render_template('instance.html', form=request.form, region=region_option, subnets=subnets, sgs=sgs, extra=extra, message=message, instances=instances)

if __name__ == "__main__":
    app.run(
        host="localhost",
        port="8081",
        debug=False
    )