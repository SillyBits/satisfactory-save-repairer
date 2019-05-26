"""
Stuff used to validate those stored objects
"""

import math


class Validator:
	
	def __init__(self, savegame):
		self.__savegame = savegame
		
	def validate(self, callback):
		self.__callback = callback

		self.__count = 0
		#self.__obj_map = {}
		
		self.__cb_start(self.__savegame.TotalElements)
		
		outcome = True

		for obj in self.__savegame.Objects:
			outcome &= self.__check(obj)
		
		for obj in self.__savegame.Collected:
			outcome &= self.__check(obj)

		self.__cb_end(outcome)



	'''
	Private implementation
	'''

	def __cb_start(self, total):
		if self.__callback: self.__callback.start(total)
		
	def __cb_update(self):
		self.__count += 1
		if self.__callback: self.__callback.update(self.__count)
		
	def __cb_end(self, state):
		if self.__callback: self.__callback.end(state)


	def __check(self, obj):
		outcome = True
		
		t = obj.TypeName
		if t in Validator.VALIDATORS:
			outcome &= Validator.VALIDATORS[t](self, obj)

		childs = obj.Childs
		if childs:
			outcome &= self.__check_recurs(childs)
			
		#if not outcome:
		#	obj.AddError("failed!")
		
		self.__cb_update()
		return outcome
	
	def __check_recurs(self, childs):
		outcome = True
		
		for name in childs:
			sub = childs[name]

			if isinstance(sub, (list,dict)):
				for obj in sub:
					outcome &= self.__check(obj)
			else:
				outcome &= self.__check(sub)

		return outcome

	'''
	Actual validators
	'''

	LOWER_SCALE = +1.0e-10
	LOWER_BOUND = -1.0e+10
	UPPER_BOUND = +1.0e+10

	@staticmethod
	def __add_error(obj, params=None):
		s = "Invalid " + obj.TypeName
		if params:
			s += ": " + params
		obj.AddError(s)


	@staticmethod	
	def __is_valid(val, lowerbounds=None, upperbounds=None):
		#global LOWER_BOUND, UPPER_BOUND
		if val is None or val == math.inf or val == math.nan:
			return False
		limit = lowerbounds or Validator.LOWER_BOUND
		if val <= limit:
			return False
		limit = upperbounds or Validator.UPPER_BOUND
		if val >= limit:
			return False
		return True
		
	@staticmethod	
	def __v_3(obj, a,b,c, lowerbounds=None, upperbounds=None):
		if not (Validator.__is_valid(a, lowerbounds, upperbounds) or \
				Validator.__is_valid(b, lowerbounds, upperbounds) or \
				Validator.__is_valid(c, lowerbounds, upperbounds)):
			#obj.AddError("Invalid {}: {} | {} | {}"\
			#		.format(obj.TypeName, a, b, c))
			Validator.__add_error(obj, 
				"{} | {} | {}".format(obj.TypeName, a, b, c))
			return False
		return True
		
	@staticmethod	
	def __v_4(obj, a,b,c,d, lowerbounds=None, upperbounds=None):
		if not (Validator.__is_valid(a, lowerbounds, upperbounds) or \
				Validator.__is_valid(b, lowerbounds, upperbounds) or \
				Validator.__is_valid(c, lowerbounds, upperbounds) or \
				Validator.__is_valid(d, lowerbounds, upperbounds)):
			#obj.AddError("Invalid {}: {} | {} | {} | {}"\
			#		.format(obj.TypeName, a, b, c, d))
			Validator.__add_error(obj, 
				"{} | {} | {} | {}".format(obj.TypeName, a, b, c, d))
			return False
		return True


	def __v_Vector(self, obj, lowerbounds=None):
		#if not Validator.isValidVec3(obj.X, obj.Y, obj.Z):
		#	obj.AddError("Invalid Vector: {} | {} | {}"\
		#			.format(obj.X, obj.Y, obj.Z))
		#	return False
		#return True
		return Validator.__v_3(obj, obj.X,obj.Y,obj.Z, lowerbounds)

	def __v_Rotator(self, obj):
		return Validator.__v_3(obj, obj.X,obj.Y,obj.Z)
	
	#def __v_Transform(self, obj):
	#	#TODO: It's actually a list containing trans, rot + scale
	#	return True

	def __v_Quat(self, obj):
		if obj.D is None:
			return Validator.__v_3(obj, obj.A,obj.B,obj.C)
		return Validator.__v_4(obj, obj.A,obj.B,obj.C,obj.D)

	def __v_Actor(self, obj):
		outcome = True
		if obj.NeedTransform:
			if not self.__v_Quat(obj.Rotation):
				#obj.AddError("Invalid " + obj.Rotation.TypeName)
				Validator.__add_error(obj, "Property 'Rotation'")
				outcome = False
			if not self.__v_Vector(obj.Translate):
				#obj.AddError("Invalid " + obj.Translate.TypeName)
				Validator.__add_error(obj, "Property 'Translate'")
				outcome = False
			# For now, we print negative scales as error
			if not self.__v_Vector(obj.Scale, Validator.LOWER_SCALE):
				#obj.AddError("Invalid " + obj.Scale.TypeName)
				Validator.__add_error(obj, "Property 'Scale'")
				outcome = False
		return outcome
		

	VALIDATORS = {
		#'Property': 			__v_Property,
		#'PropertyList': 		__v_PropertyList,
		#'BoolProperty': 		__v_BoolProperty,
		#'ByteProperty': 		__v_ByteProperty,
		#'IntProperty': 			__v_IntProperty,
		#'FloatProperty': 		__v_FloatProperty,
		#'StrProperty': 			__v_StrProperty,
		#'Header': 				__v_Header,
		#'Collected': 			__v_Collected,
		#'StructProperty': 		__v_StructProperty,
		'Vector':				__v_Vector,
		'Rotator': 				__v_Rotator,
		#'Box': 					__v_Box,
		#'Color': 				__v_Color,
		#'LinearColor': 			__v_LinearColor,
		#'Transform': 			__v_Transform,
		'Quat': 				__v_Quat,
		#'RemovedInstanceArray': __v_RemovedInstanceArray,
		#'RemovedInstance': 		__v_RemovedInstance,
		#'InventoryStack': 		__v_InventoryStack,
		#'InventoryItem': 		__v_InventoryItem,
		#'PhaseCost': 			__v_PhaseCost,
		#'ItemAmount':			__v_ItemAmount,
		#'ResearchCost': 		__v_ResearchCost,
		#'CompletedResearch': 	__v_CompletedResearch,
		#'ResearchRecipeReward': __v_ResearchRecipeReward,
		#'ItemFoundData': 		__v_ItemFoundData,
		#'RecipeAmountStruct': 	__v_RecipeAmountStruct,
		#'MessageData': 			__v_MessageData,
		#'SplinePointData': 		__v_SplinePointData,
		#'SpawnData': 			__v_SpawnData,
		#'FeetOffset':			__v_FeetOffset,
		#'SplitterSortRule': 	__v_SplitterSortRule,
		#'ArrayProperty': 		__v_ArrayProperty,
		#'ObjectProperty': 		__v_ObjectProperty,
		#'EnumProperty': 		__v_EnumProperty,
		#'NameProperty': 		__v_NameProperty,
		#'MapProperty': 			__v_MapProperty,
		#'TextProperty': 		__v_TextProperty,
		#'Entity': 				__v_Entity,
		#'NamedEntity': 			__v_NamedEntity,
		#'Object': 				__v_Object,
		'Actor': 				__v_Actor,
		}
