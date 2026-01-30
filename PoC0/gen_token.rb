r=Ci::Runner.new
r.runner_type='instance_type'
r.description='Docker-Runner-PoC'
r.tag_list=['docker', 'shadow-file']
r.run_untagged=true
r.locked=false
r.access_level='not_protected'
r.save!
print r.token
